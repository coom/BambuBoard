import sqlite3
from datetime import datetime, timedelta


# Calcule la consommation réelle en sommant uniquement les décroissances
_CONSUMPTION_CTE = """
WITH consecutive AS (
    SELECT
        cl.spool_id,
        cl.remain_pct AS cur_pct,
        LAG(cl.remain_pct) OVER (PARTITION BY cl.spool_id ORDER BY cl.id) AS prev_pct
    FROM consumption_logs cl
),
spool_consumed AS (
    SELECT
        spool_id,
        SUM(CASE WHEN prev_pct > cur_pct THEN prev_pct - cur_pct ELSE 0 END) AS pct_consumed
    FROM consecutive
    WHERE prev_pct IS NOT NULL
    GROUP BY spool_id
)
"""

SESSION_GAP_MINUTES = 30  # écart max entre 2 logs pour rester dans la même session


def _build_sessions(rows: list[dict]) -> list[dict]:
    """Regroupe les logs bruts en sessions d'impression.
    Chaque session = plage de temps continue par bobine (gap < SESSION_GAP_MINUTES)."""
    sessions = []
    current = None

    for r in rows:
        ts = r["logged_at"]
        try:
            dt = datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            continue

        same_spool = current and current["spool_id"] == r["spool_id"]
        if same_spool:
            gap = (current["_last_dt"] - dt).total_seconds() / 60
        else:
            gap = 999

        if same_spool and gap < SESSION_GAP_MINUTES:
            current["end_pct"] = r["remain_pct"]
            current["_last_dt"] = dt
            current["end_time"] = ts
            current["log_count"] += 1
            if not current.get("print_job") and r.get("print_job"):
                current["print_job"] = r["print_job"]
        else:
            if current:
                _finalize(current)
                sessions.append(current)
            current = {
                "spool_id": r["spool_id"],
                "name": r["name"],
                "tray_type": r["tray_type"],
                "color_hex": r["color_hex"],
                "color_name": r.get("color_name", ""),
                "initial_weight": r.get("initial_weight", 1000),
                "slot_index": r["slot_index"],
                "print_job": r.get("print_job") or None,
                "start_pct": r["remain_pct"],
                "end_pct": r["remain_pct"],
                "start_time": ts,
                "end_time": ts,
                "_last_dt": dt,
                "log_count": 1,
            }

    if current:
        _finalize(current)
        sessions.append(current)

    # Ne garder que les sessions avec consommation réelle (exclut les ajouts initiaux)
    return [s for s in sessions if s["consumed_pct"] > 0]


def _finalize(s: dict):
    """Calcule les champs dérivés d'une session."""
    # Les logs sont traités en DESC : start_pct = plus récent (bas),
    # end_pct = plus ancien (haut). On swap pour l'ordre chronologique.
    s["start_pct"], s["end_pct"] = s["end_pct"], s["start_pct"]
    s["start_time"], s["end_time"] = s["end_time"], s["start_time"]
    s["consumed_pct"] = max(0, s["start_pct"] - s["end_pct"])
    weight = s.get("initial_weight") or 1000
    s["consumed_grams"] = round(s["consumed_pct"] / 100 * weight)
    del s["_last_dt"]


LOW_STOCK_THRESHOLD = 20

def get_kpis(db: sqlite3.Connection) -> dict:
    threshold = LOW_STOCK_THRESHOLD

    # Consommation par type + couleur (grammes) — inclut toutes les bobines (même archivées)
    by_type = db.execute(_CONSUMPTION_CTE + """
        SELECT s.tray_type, s.color_hex, s.color_name, s.sub_brands,
               SUM(sc.pct_consumed * s.initial_weight / 100.0) AS grams_used
        FROM spools s
        JOIN spool_consumed sc ON sc.spool_id = s.id
        WHERE s.tray_type IS NOT NULL
        GROUP BY s.tray_type, s.color_hex, s.sub_brands
        ORDER BY grams_used DESC
    """).fetchall()

    # Consommation par marque
    by_brand = db.execute(_CONSUMPTION_CTE + """
        SELECT s.brand,
               SUM(sc.pct_consumed * s.initial_weight / 100.0) AS grams_used
        FROM spools s
        JOIN spool_consumed sc ON sc.spool_id = s.id
        WHERE s.brand IS NOT NULL
        GROUP BY s.brand
        ORDER BY grams_used DESC
    """).fetchall()

    # Coût total estimé
    cost_row = db.execute(_CONSUMPTION_CTE + """
        SELECT SUM(sc.pct_consumed * s.initial_weight / 100.0 / 1000.0 * s.price_per_kg) AS total_cost
        FROM spools s
        JOIN spool_consumed sc ON sc.spool_id = s.id
        WHERE s.price_per_kg IS NOT NULL
    """).fetchone()

    # Bobines low stock (≤ seuil) — uniquement actives et idle
    low_stock = db.execute("""
        SELECT s.id, s.name, s.tray_type, s.color_hex, s.color_name, s.status,
               a.remain_pct, a.slot_index
        FROM spools s
        JOIN ams_state a ON a.tray_uuid = s.tray_uuid
        WHERE a.remain_pct <= ? AND s.status IN ('active', 'idle')
        UNION
        SELECT s.id, s.name, s.tray_type, s.color_hex, s.color_name, s.status,
               l.remain_pct, NULL
        FROM spools s
        JOIN (
            SELECT spool_id, remain_pct,
                   ROW_NUMBER() OVER (PARTITION BY spool_id ORDER BY id DESC) AS rn
            FROM consumption_logs
        ) l ON l.spool_id = s.id AND l.rn = 1
        WHERE l.remain_pct <= ?
          AND s.status IN ('active', 'idle')
          AND (s.tray_uuid IS NULL OR s.tray_uuid NOT IN (
              SELECT tray_uuid FROM ams_state WHERE tray_uuid IS NOT NULL
          ))
        ORDER BY remain_pct ASC
    """, (threshold, threshold)).fetchall()

    # Sessions d'impression
    recent_raw = db.execute("""
        SELECT cl.id, cl.spool_id, s.name, s.tray_type, s.color_hex, s.color_name,
               s.initial_weight, cl.slot_index, cl.remain_pct, cl.logged_at, cl.print_job
        FROM consumption_logs cl
        JOIN spools s ON s.id = cl.spool_id
        ORDER BY cl.id DESC
        LIMIT 100
    """).fetchall()

    sessions = _build_sessions([dict(r) for r in recent_raw])

    # Compteurs par statut
    counts = db.execute("""
        SELECT status, COUNT(*) as cnt FROM spools GROUP BY status
    """).fetchall()
    stock = {"active": 0, "idle": 0, "empty": 0, "archived": 0}
    for r in counts:
        stock[r["status"] or "active"] = r["cnt"]

    # Compteur "dans AMS" basé sur la présence réelle dans ams_state (pas le statut DB)
    in_ams = db.execute("""
        SELECT COUNT(*) as cnt
        FROM spools s
        JOIN ams_state a ON a.tray_uuid = s.tray_uuid
        WHERE s.tray_uuid IS NOT NULL
          AND a.tray_uuid IS NOT NULL
          AND s.status NOT IN ('archived')
    """).fetchone()["cnt"]

    # "rangées" = bobines non-archivées, non-vides, pas dans l'AMS
    in_stock = db.execute("""
        SELECT COUNT(*) as cnt
        FROM spools s
        WHERE s.status IN ('active', 'idle')
          AND (s.tray_uuid IS NULL OR s.tray_uuid NOT IN (
              SELECT tray_uuid FROM ams_state WHERE tray_uuid IS NOT NULL
          ))
    """).fetchone()["cnt"]

    return {
        "by_type": [dict(r) for r in by_type if (r["grams_used"] or 0) > 0],
        "by_brand": [dict(r) for r in by_brand if (r["grams_used"] or 0) > 0],
        "total_cost": round(cost_row["total_cost"] or 0, 2),
        "low_stock": [dict(r) for r in low_stock],
        "low_stock_threshold": threshold,
        "sessions": sessions[:15],
        "stock": stock,
        "in_ams": in_ams,
        "in_stock": in_stock,
        "spool_count": in_ams + in_stock,
    }
