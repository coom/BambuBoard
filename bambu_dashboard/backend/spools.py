import sqlite3
from typing import Optional

import config as cfg


def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def list_spools(db: sqlite3.Connection, status_filter: str = None) -> list[dict]:
    """Liste les bobines. status_filter: 'active', 'idle', 'empty', 'archived' ou None (toutes sauf archived)."""
    if status_filter:
        rows = db.execute("""
            SELECT s.*,
                   a.slot_index AS ams_slot,
                   a.remain_pct AS current_remain
            FROM spools s
            LEFT JOIN ams_state a ON a.tray_uuid = s.tray_uuid
            WHERE s.status = ?
            ORDER BY s.created_at DESC
        """, (status_filter,)).fetchall()
    else:
        rows = db.execute("""
            SELECT s.*,
                   a.slot_index AS ams_slot,
                   a.remain_pct AS current_remain
            FROM spools s
            LEFT JOIN ams_state a ON a.tray_uuid = s.tray_uuid
            WHERE s.status != 'archived'
            ORDER BY s.created_at DESC
        """).fetchall()

    result = []
    for row in rows:
        d = _row_to_dict(row)
        remain = d.get("current_remain")
        if remain is None:
            last = db.execute(
                "SELECT remain_pct FROM consumption_logs WHERE spool_id=? ORDER BY id DESC LIMIT 1",
                (d["id"],)
            ).fetchone()
            remain = last["remain_pct"] if last else d.get("initial_remain", 100)
        d["current_remain"] = remain
        d["weight_remaining"] = round(remain / 100 * (d["initial_weight"] or 1000))
        result.append(d)
    return result


def get_spool(db: sqlite3.Connection, spool_id: int) -> Optional[dict]:
    row = db.execute("SELECT * FROM spools WHERE id=?", (spool_id,)).fetchone()
    return _row_to_dict(row) if row else None


def find_by_tray_uuid(db: sqlite3.Connection, tray_uuid: str) -> Optional[dict]:
    row = db.execute("SELECT * FROM spools WHERE tray_uuid=?", (tray_uuid,)).fetchone()
    return _row_to_dict(row) if row else None


def create_spool(db: sqlite3.Connection, data: dict) -> dict:
    fields = ["tray_uuid", "tag_uid", "name", "brand", "tray_type", "sub_brands",
              "color_name", "color_hex", "filament_code", "initial_weight",
              "price_per_kg", "initial_remain", "status", "ams_sync"]
    values = {f: data.get(f) for f in fields}
    if values["initial_remain"] is None:
        values["initial_remain"] = 100
    if values["status"] is None:
        values["status"] = "active"
    cur = db.execute(
        f"INSERT INTO spools ({','.join(values.keys())}) VALUES ({','.join('?' * len(values))})",
        list(values.values())
    )
    db.commit()
    spool_id = cur.lastrowid
    initial_remain = values["initial_remain"] or 100
    db.execute(
        "INSERT INTO consumption_logs (spool_id, slot_index, remain_pct) VALUES (?,?,?)",
        (spool_id, None, initial_remain)
    )
    db.commit()
    return get_spool(db, spool_id)


def update_spool(db: sqlite3.Connection, spool_id: int, data: dict) -> Optional[dict]:
    fields = ["tray_uuid", "tag_uid", "name", "brand", "tray_type", "sub_brands",
              "color_name", "color_hex", "filament_code", "initial_weight",
              "price_per_kg", "initial_remain", "status", "ams_sync"]
    updates = {f: data[f] for f in fields if f in data}
    if not updates:
        return get_spool(db, spool_id)
    db.execute(
        f"UPDATE spools SET {', '.join(f'{k}=?' for k in updates)} WHERE id=?",
        [*updates.values(), spool_id]
    )
    db.commit()
    return get_spool(db, spool_id)


def set_status(db: sqlite3.Connection, spool_id: int, status: str) -> Optional[dict]:
    """Change le statut d'une bobine (active, idle, empty, archived)."""
    if status not in ("active", "idle", "empty", "archived"):
        return None
    spool = get_spool(db, spool_id)
    if not spool:
        return None
    # Si on archive, détacher du tray_uuid pour libérer le slot
    if status == "archived":
        db.execute("UPDATE spools SET status=?, tray_uuid=NULL WHERE id=?", (status, spool_id))
    else:
        db.execute("UPDATE spools SET status=? WHERE id=?", (status, spool_id))
    db.commit()
    return get_spool(db, spool_id)


def rebuy_spool(db: sqlite3.Connection, spool_id: int) -> Optional[dict]:
    """Duplique une bobine (rachat) : archive l'ancienne, crée une nouvelle identique à 100%."""
    old = get_spool(db, spool_id)
    if not old:
        return None
    # Archiver l'ancienne
    db.execute("UPDATE spools SET status='archived', tray_uuid=NULL WHERE id=?", (spool_id,))
    db.commit()
    # Créer la nouvelle
    new_data = {
        "name": old["name"],
        "brand": old.get("brand"),
        "tray_type": old.get("tray_type"),
        "sub_brands": old.get("sub_brands"),
        "color_name": old.get("color_name"),
        "color_hex": old.get("color_hex"),
        "filament_code": old.get("filament_code"),
        "initial_weight": old.get("initial_weight") or 1000,
        "price_per_kg": old.get("price_per_kg"),
        "initial_remain": 100,
        "status": "idle",
    }
    return create_spool(db, new_data)


def delete_spool(db: sqlite3.Connection, spool_id: int) -> bool:
    """Suppression définitive (avec cascade des logs)."""
    cur = db.execute("DELETE FROM spools WHERE id=?", (spool_id,))
    db.commit()
    return cur.rowcount > 0


def log_consumption(db: sqlite3.Connection, spool_id: int, slot_index: Optional[int], remain_pct: int):
    db.execute(
        "INSERT INTO consumption_logs (spool_id, slot_index, remain_pct) VALUES (?,?,?)",
        (spool_id, slot_index, remain_pct)
    )
    db.commit()


def snapshot_spool(db: sqlite3.Connection, spool_id: int) -> Optional[dict]:
    """Force un snapshot du remain courant depuis l'AMS ou le dernier log connu."""
    spool = get_spool(db, spool_id)
    if not spool:
        return None
    ams_row = None
    if spool.get("tray_uuid"):
        ams_row = db.execute(
            "SELECT remain_pct, slot_index FROM ams_state WHERE tray_uuid=?",
            (spool["tray_uuid"],)
        ).fetchone()
    if ams_row:
        log_consumption(db, spool_id, ams_row["slot_index"], ams_row["remain_pct"])
        return {"spool_id": spool_id, "remain_pct": ams_row["remain_pct"], "source": "ams"}
    last = db.execute(
        "SELECT remain_pct FROM consumption_logs WHERE spool_id=? ORDER BY id DESC LIMIT 1",
        (spool_id,)
    ).fetchone()
    remain = last["remain_pct"] if last else spool.get("initial_remain", 100)
    log_consumption(db, spool_id, None, remain)
    return {"spool_id": spool_id, "remain_pct": remain, "source": "last_known"}


def update_ams_state(db: sqlite3.Connection, slot_index: int, tray_uuid: Optional[str], tag_uid: Optional[str], remain_pct: int):
    db.execute("""
        INSERT INTO ams_state (slot_index, tray_uuid, tag_uid, remain_pct, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(slot_index) DO UPDATE SET
            tray_uuid=excluded.tray_uuid,
            tag_uid=excluded.tag_uid,
            remain_pct=excluded.remain_pct,
            updated_at=excluded.updated_at
    """, (slot_index, tray_uuid, tag_uid, remain_pct))
    db.commit()


def get_consumption_history(db: sqlite3.Connection, spool_id: int) -> list[dict]:
    rows = db.execute(
        "SELECT * FROM consumption_logs WHERE spool_id=? ORDER BY id DESC LIMIT 50",
        (spool_id,)
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_stock_summary(db: sqlite3.Connection) -> dict:
    """Résumé du stock pour le dashboard."""
    counts = db.execute("""
        SELECT status, COUNT(*) as cnt
        FROM spools
        GROUP BY status
    """).fetchall()
    summary = {"active": 0, "idle": 0, "empty": 0, "archived": 0, "total": 0}
    for r in counts:
        s = r["status"] or "active"
        summary[s] = r["cnt"]
    summary["total"] = summary["active"] + summary["idle"] + summary["empty"]
    return summary
