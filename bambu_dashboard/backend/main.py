import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from printer import printer_manager
from database import init_db, get_db
import spools as spool_service
import kpis as kpi_service
import config as cfg
import notifications as notif_service
import time as _time

# ── NFC scan pending store ────────────────────────────────────────────────────
_pending_nfc_scan: dict | None = None


def _process_and_enrich(db, ams_data: dict):
    """Détecte les changements de remain, log la consommation, gère les statuts,
    et enrichit chaque slot avec son spool. Tout en une passe, un seul commit."""
    if not ams_data.get("connected"):
        return

    slots = ams_data.get("slots", [])
    tray_uuids = [s.get("tray_uuid") for s in slots if s.get("tray_uuid")]

    # Batch fetch de tous les spools concernés
    spools_by_uuid = {}
    if tray_uuids:
        placeholders = ",".join("?" * len(tray_uuids))
        rows = db.execute(
            f"SELECT * FROM spools WHERE tray_uuid IN ({placeholders})",
            tray_uuids,
        ).fetchall()
        spools_by_uuid = {r["tray_uuid"]: dict(r) for r in rows}

    # Batch fetch du dernier log pour chaque spool concerné
    last_logs = {}
    if spools_by_uuid:
        spool_ids = [s["id"] for s in spools_by_uuid.values()]
        placeholders = ",".join("?" * len(spool_ids))
        rows = db.execute(
            f"""SELECT spool_id, remain_pct FROM consumption_logs
                WHERE id IN (
                    SELECT MAX(id) FROM consumption_logs
                    WHERE spool_id IN ({placeholders})
                    GROUP BY spool_id
                )""",
            spool_ids,
        ).fetchall()
        last_logs = {r["spool_id"]: r["remain_pct"] for r in rows}

    dirty = False
    notifications = []

    # ── Auto-détection : bobines qui étaient dans l'AMS mais n'y sont plus ──
    current_ams_uuids = set(tray_uuids)
    previous_ams = db.execute(
        "SELECT tray_uuid FROM ams_state WHERE tray_uuid IS NOT NULL"
    ).fetchall()
    previous_ams_uuids = {r["tray_uuid"] for r in previous_ams}

    removed_uuids = previous_ams_uuids - current_ams_uuids
    if removed_uuids:
        placeholders = ",".join("?" * len(removed_uuids))
        # Bobines retirées de l'AMS → passer en idle (ou empty si ≤ seuil)
        removed_spools = db.execute(
            f"SELECT id, status, tray_uuid FROM spools WHERE tray_uuid IN ({placeholders}) AND status = 'active'",
            list(removed_uuids),
        ).fetchall()
        for rs in removed_spools:
            last = db.execute(
                "SELECT remain_pct FROM consumption_logs WHERE spool_id=? ORDER BY id DESC LIMIT 1",
                (rs["id"],)
            ).fetchone()
            remain = last["remain_pct"] if last else 100
            new_status = "empty" if remain <= 5 else "idle"
            db.execute("UPDATE spools SET status=? WHERE id=?", (new_status, rs["id"]))
            dirty = True

    for slot in slots:
        tray_uuid = slot.get("tray_uuid")
        tag_uid = slot.get("tag_uid")
        remain = slot.get("remain")
        idx = slot.get("index")

        spool = spools_by_uuid.get(tray_uuid) if tray_uuid else None
        slot["spool"] = spool

        if remain is None:
            continue

        # Clamp : l'AMS peut estimer des valeurs negatives
        remain = max(0, remain)

        # Réconciliation tag_uid → tray_uuid pour bobines déjà enregistrées
        if tray_uuid and tag_uid:
            db.execute("""
                UPDATE spools SET tray_uuid = ?
                WHERE tag_uid = ? AND (tray_uuid IS NULL OR tray_uuid = '')
            """, (tray_uuid, tag_uid))
            dirty = True

        # Si la bobine a ams_sync=0, ne pas écraser remain_pct
        skip_remain = spool and spool.get("ams_sync") == 0

        # Mise à jour de l'état du slot (sauf remain_pct si sync désactivée)
        if skip_remain:
            db.execute("""
                INSERT INTO ams_state (slot_index, tray_uuid, tag_uid, remain_pct, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                ON CONFLICT(slot_index) DO UPDATE SET
                    tray_uuid=excluded.tray_uuid,
                    tag_uid=excluded.tag_uid,
                    updated_at=excluded.updated_at
            """, (idx, tray_uuid, tag_uid, remain))
        else:
            db.execute("""
                INSERT INTO ams_state (slot_index, tray_uuid, tag_uid, remain_pct, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                ON CONFLICT(slot_index) DO UPDATE SET
                    tray_uuid=excluded.tray_uuid,
                    tag_uid=excluded.tag_uid,
                    remain_pct=excluded.remain_pct,
                    updated_at=excluded.updated_at
            """, (idx, tray_uuid, tag_uid, remain))
        dirty = True

        if not spool:
            continue

        # Auto-activation : bobine idle/empty remise dans l'AMS → active
        if spool.get("status") in ("idle", "empty"):
            db.execute("UPDATE spools SET status='active' WHERE id=?", (spool["id"],))
            dirty = True

        last_pct = last_logs.get(spool["id"])

        if last_pct is None:
            db.execute(
                "INSERT INTO consumption_logs (spool_id, slot_index, remain_pct) VALUES (?,?,?)",
                (spool["id"], idx, remain),
            )
            dirty = True
        elif not skip_remain and last_pct > remain and (last_pct - remain) >= 2:
            db.execute(
                "INSERT INTO consumption_logs (spool_id, slot_index, remain_pct) VALUES (?,?,?)",
                (spool["id"], idx, remain),
            )
            dirty = True

            # Notification stock faible
            threshold = cfg.LOW_STOCK_THRESHOLD
            if remain <= threshold and last_pct > threshold:
                notifications.append({
                    "spool_name": spool["name"],
                    "tray_type": spool.get("tray_type") or "",
                    "color_name": spool.get("color_name") or "",
                    "remain_pct": remain,
                })

            # Auto-empty : bobine à 0%
            if remain <= 0:
                db.execute("UPDATE spools SET status='empty' WHERE id=?", (spool["id"],))

    if dirty:
        db.commit()

    for n in notifications:
        notif_service.notify_low_spool(**n)


def _enrich_callback(data: dict):
    """Appelé par le thread MQTT à chaque message AMS reçu."""
    db = get_db()
    try:
        _process_and_enrich(db, data)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    printer_manager.reconfigure(cfg.PRINTER_IP, cfg.PRINTER_ACCESS_CODE, cfg.PRINTER_SERIAL)
    printer_manager.connect(enrich_callback=_enrich_callback)
    yield
    printer_manager.disconnect()


app = FastAPI(lifespan=lifespan)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


# ── AMS ──────────────────────────────────────────────────────────────────────

@app.get("/api/ams")
def get_ams():
    return printer_manager.get_ams_data()


# ── Spools CRUD ───────────────────────────────────────────────────────────────

@app.get("/api/spools")
def list_spools(status: str = Query(None)):
    db = get_db()
    try:
        return spool_service.list_spools(db, status_filter=status)
    finally:
        db.close()


@app.get("/api/spools/summary")
def stock_summary():
    db = get_db()
    try:
        return spool_service.get_stock_summary(db)
    finally:
        db.close()


@app.get("/api/spools/match/{tray_uuid}")
def match_spool(tray_uuid: str):
    db = get_db()
    try:
        spool = spool_service.find_by_tray_uuid(db, tray_uuid)
        if not spool:
            raise HTTPException(status_code=404, detail="Bobine non trouvée")
        return spool
    finally:
        db.close()


@app.post("/api/spools", status_code=201)
def create_spool(data: dict):
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Le champ 'name' est requis")
    db = get_db()
    try:
        return spool_service.create_spool(db, data)
    finally:
        db.close()


@app.put("/api/spools/{spool_id}")
def update_spool(spool_id: int, data: dict):
    db = get_db()
    try:
        manual_remain = data.pop("manual_remain", None)
        spool = spool_service.update_spool(db, spool_id, data)
        if not spool:
            raise HTTPException(status_code=404, detail="Bobine non trouvée")
        # Si ams_sync=0 et manual_remain fourni, écrire la valeur calibrée
        if data.get("ams_sync") == 0 and manual_remain is not None:
            pct = max(0, min(100, int(manual_remain)))
            spool_service.log_consumption(db, spool_id, None, pct)
            tray_uuid = spool.get("tray_uuid")
            if tray_uuid:
                db.execute(
                    "UPDATE ams_state SET remain_pct=? WHERE tray_uuid=?",
                    (pct, tray_uuid)
                )
                db.commit()
        return spool
    finally:
        db.close()


@app.put("/api/spools/{spool_id}/status")
def change_status(spool_id: int, data: dict):
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Le champ 'status' est requis")
    db = get_db()
    try:
        spool = spool_service.set_status(db, spool_id, status)
        if not spool:
            raise HTTPException(status_code=400, detail="Statut invalide ou bobine non trouvée")
        return spool
    finally:
        db.close()


@app.post("/api/spools/{spool_id}/rebuy")
def rebuy_spool(spool_id: int):
    db = get_db()
    try:
        new_spool = spool_service.rebuy_spool(db, spool_id)
        if not new_spool:
            raise HTTPException(status_code=404, detail="Bobine non trouvée")
        return new_spool
    finally:
        db.close()


@app.delete("/api/spools/{spool_id}", status_code=204)
def delete_spool(spool_id: int):
    db = get_db()
    try:
        if not spool_service.delete_spool(db, spool_id):
            raise HTTPException(status_code=404, detail="Bobine non trouvée")
    finally:
        db.close()


@app.get("/api/consumption/{spool_id}")
def consumption_history(spool_id: int):
    db = get_db()
    try:
        return spool_service.get_consumption_history(db, spool_id)
    finally:
        db.close()


@app.post("/api/spools/{spool_id}/snapshot")
def snapshot_spool(spool_id: int):
    db = get_db()
    try:
        result = spool_service.snapshot_spool(db, spool_id)
        if not result:
            raise HTTPException(status_code=404, detail="Bobine non trouvée")
        return result
    finally:
        db.close()



@app.get("/api/spools/export.csv")
def export_csv():
    from fastapi.responses import Response
    db = get_db()
    try:
        spools = spool_service.list_spools(db)
        lines = ["id,name,brand,tray_type,sub_brands,color_name,color_hex,filament_code,initial_weight,initial_remain,current_remain,weight_remaining,price_per_kg,status,tag_uid,created_at"]
        for s in spools:
            def esc(v): return f'"{str(v or "").replace(chr(34), chr(39))}"'
            lines.append(",".join([
                esc(s.get("id")), esc(s.get("name")), esc(s.get("brand")),
                esc(s.get("tray_type")), esc(s.get("sub_brands")), esc(s.get("color_name")),
                esc(s.get("color_hex")), esc(s.get("filament_code")),
                esc(s.get("initial_weight")), esc(s.get("initial_remain")),
                esc(s.get("current_remain")), esc(s.get("weight_remaining")),
                esc(s.get("price_per_kg")), esc(s.get("status")),
                esc(s.get("tag_uid")), esc(s.get("created_at"))
            ]))
        csv = "\n".join(lines)
        return Response(content=csv, media_type="text/csv",
                        headers={"Content-Disposition": "attachment; filename=bobines.csv"})
    finally:
        db.close()


# ── Reset ─────────────────────────────────────────────────────────────────────

@app.post("/api/admin/reset-data")
def reset_data():
    """Vide consumption_logs et ams_state — conserve les bobines."""
    db = get_db()
    try:
        db.execute("DELETE FROM consumption_logs")
        db.execute("DELETE FROM ams_state")
        db.commit()
        return {"status": "ok", "message": "Historique et états AMS effacés"}
    finally:
        db.close()


@app.post("/api/admin/reset-all")
def reset_all():
    """Remet tout à zéro — bobines, historique, états AMS."""
    db = get_db()
    try:
        db.execute("DELETE FROM consumption_logs")
        db.execute("DELETE FROM ams_state")
        db.execute("DELETE FROM spools")
        db.commit()
        return {"status": "ok", "message": "Base de données complètement réinitialisée"}
    finally:
        db.close()


# ── KPIs ─────────────────────────────────────────────────────────────────────

@app.get("/api/kpis")
def get_kpis():
    db = get_db()
    try:
        return kpi_service.get_kpis(db)
    finally:
        db.close()


# ── NFC Scan (Flipper Zero) ───────────────────────────────────────────────────

@app.post("/api/nfc/push", status_code=200)
def nfc_push(data: dict):
    """Reçoit les données NFC depuis le Flipper Zero et les stocke temporairement."""
    global _pending_nfc_scan
    required = {"tag_uid", "tray_type"}
    if not required.issubset(data.keys()):
        raise HTTPException(status_code=400, detail="Champs requis : tag_uid, tray_type")
    _pending_nfc_scan = {"data": data, "ts": _time.time()}
    return {"ok": True}


@app.get("/api/nfc/pending")
def nfc_pending():
    """Poll par le frontend — retourne et vide les données NFC si disponibles (< 60s)."""
    global _pending_nfc_scan
    scan = _pending_nfc_scan
    _pending_nfc_scan = None
    if scan is None:
        return Response(status_code=204)
    if _time.time() - scan["ts"] > 60:
        return Response(status_code=204)
    scan_data = scan["data"]

    # Vérifier si la bobine existe déjà par tag_uid
    tag_uid = scan_data.get("tag_uid")
    db = get_db()
    try:
        existing = db.execute(
            "SELECT * FROM spools WHERE tag_uid = ?", (tag_uid,)
        ).fetchone()
        existing_spool = dict(existing) if existing else None
    finally:
        db.close()

    return {
        "data": scan_data,
        "exists": existing_spool is not None,
        "existing_spool": existing_spool,
    }


# ── Config (lecture seule pour le frontend) ──────────────────────────────────

@app.get("/api/config")
def get_config():
    return {"low_stock_threshold": cfg.LOW_STOCK_THRESHOLD}


@app.get("/api/debug")
def debug_info():
    import hashlib
    frontend_path = os.path.join(FRONTEND_DIR, "index.html")
    overlay_path = "/share/bambu_dashboard/frontend/index.html"
    frontend_hash = ""
    frontend_size = 0
    overlay_exists = os.path.exists(overlay_path)
    overlay_hash = ""
    try:
        with open(frontend_path, "rb") as f:
            data = f.read()
            frontend_hash = hashlib.md5(data).hexdigest()
            frontend_size = len(data)
    except Exception:
        pass
    if overlay_exists:
        try:
            with open(overlay_path, "rb") as f:
                overlay_hash = hashlib.md5(f.read()).hexdigest()
        except Exception:
            pass
    return {
        "version": "1.0.10",
        "frontend_path": frontend_path,
        "frontend_size": frontend_size,
        "frontend_md5": frontend_hash,
        "overlay_active": overlay_exists,
        "overlay_path": overlay_path if overlay_exists else None,
        "overlay_md5": overlay_hash or None,
        "overlay_warning": "L'overlay ecrase le frontend embarque !" if overlay_exists else None,
        "db_path": database.DB_PATH,
    }


# ── Notifications ────────────────────────────────────────────────────────────

@app.post("/api/notifications/test")
def test_notification():
    result = notif_service.notify_low_spool(
        spool_name="Test Bobine",
        tray_type="PLA",
        color_name="Rouge",
        remain_pct=18,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "Erreur inconnue"))
    return result


# ── Static ────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    return FileResponse(
        os.path.join(FRONTEND_DIR, "index.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"},
    )


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["."])
