import sqlite3
import os

DB_PATH = os.environ.get(
    "BAMBU_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "bambu.db"),
)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    return conn


def _migrate(conn):
    """Migrations pour les bases existantes."""
    spools_cols = {r[1] for r in conn.execute("PRAGMA table_info(spools)")}
    if "tray_uuid" not in spools_cols:
        conn.execute("ALTER TABLE spools ADD COLUMN tray_uuid TEXT")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_spools_tray_uuid ON spools(tray_uuid) WHERE tray_uuid IS NOT NULL")
        conn.commit()
    if "initial_remain" not in spools_cols:
        conn.execute("ALTER TABLE spools ADD COLUMN initial_remain INTEGER DEFAULT 100")
        conn.commit()
    if "status" not in spools_cols:
        conn.execute("ALTER TABLE spools ADD COLUMN status TEXT DEFAULT 'active'")
        conn.commit()

    ams_cols = {r[1] for r in conn.execute("PRAGMA table_info(ams_state)")}
    if "tray_uuid" not in ams_cols:
        conn.execute("ALTER TABLE ams_state ADD COLUMN tray_uuid TEXT")
        conn.commit()
    if "tag_uid" not in ams_cols:
        conn.execute("ALTER TABLE ams_state ADD COLUMN tag_uid TEXT")
        conn.commit()
    if "ams_sync" not in spools_cols:
        conn.execute("ALTER TABLE spools ADD COLUMN ams_sync INTEGER DEFAULT 1")
        conn.commit()
    if "package_type" not in spools_cols:
        conn.execute("ALTER TABLE spools ADD COLUMN package_type TEXT DEFAULT 'full'")
        conn.commit()

    logs_cols = {r[1] for r in conn.execute("PRAGMA table_info(consumption_logs)")}
    if "print_job" not in logs_cols:
        conn.execute("ALTER TABLE consumption_logs ADD COLUMN print_job TEXT")
        conn.commit()

    # Normaliser les tag_uid longs (AMS envoie 16 chars, NFC scanners 8)
    # On tronque à 8 chars (4 octets UID MIFARE) pour éviter les doublons
    conn.execute("UPDATE spools SET tag_uid = UPPER(SUBSTR(tag_uid, 1, 8)) WHERE LENGTH(tag_uid) > 8")
    conn.execute("UPDATE ams_state SET tag_uid = UPPER(SUBSTR(tag_uid, 1, 8)) WHERE LENGTH(tag_uid) > 8")
    conn.commit()

    # Corriger les faux logs de consommation : quand une bobine créée via NFC
    # (log initial à 100%, slot_index NULL) est ensuite vue par l'AMS à un %
    # inférieur, le delta est faussement compté comme consommation.
    # On aligne le log initial au premier log AMS pour annuler le faux delta.
    false_baselines = conn.execute("""
        SELECT cl_init.id AS init_id, cl_ams.remain_pct AS ams_pct
        FROM consumption_logs cl_init
        JOIN consumption_logs cl_ams ON cl_ams.spool_id = cl_init.spool_id
        WHERE cl_init.slot_index IS NULL
          AND cl_ams.slot_index IS NOT NULL
          AND cl_init.id = (
              SELECT MIN(id) FROM consumption_logs WHERE spool_id = cl_init.spool_id
          )
          AND cl_ams.id = (
              SELECT MIN(id) FROM consumption_logs
              WHERE spool_id = cl_init.spool_id AND slot_index IS NOT NULL
          )
          AND cl_init.remain_pct > cl_ams.remain_pct
    """).fetchall()
    for row in false_baselines:
        conn.execute("UPDATE consumption_logs SET remain_pct = ? WHERE id = ?",
                     (row["ams_pct"], row["init_id"]))
    if false_baselines:
        conn.commit()

    # Dédoublonner les spools qui ont le même tag_uid après normalisation :
    # garder le plus ancien (id le plus petit), transférer les logs, supprimer les doublons
    dupes = conn.execute("""
        SELECT tag_uid, MIN(id) as keep_id, GROUP_CONCAT(id) as all_ids
        FROM spools
        WHERE tag_uid IS NOT NULL AND tag_uid != ''
        GROUP BY tag_uid
        HAVING COUNT(*) > 1
    """).fetchall()
    for row in dupes:
        keep_id = row["keep_id"]
        all_ids = [int(x) for x in row["all_ids"].split(",")]
        dup_ids = [x for x in all_ids if x != keep_id]
        # Transférer les logs de consommation vers la bobine conservée
        for dup_id in dup_ids:
            conn.execute("UPDATE consumption_logs SET spool_id = ? WHERE spool_id = ?",
                         (keep_id, dup_id))
        # Copier tray_uuid du doublon si la bobine conservée n'en a pas
        conn.execute("""
            UPDATE spools SET tray_uuid = (
                SELECT tray_uuid FROM spools s2
                WHERE s2.id IN ({}) AND s2.tray_uuid IS NOT NULL AND s2.tray_uuid != ''
                LIMIT 1
            ) WHERE id = ? AND (tray_uuid IS NULL OR tray_uuid = '')
        """.format(",".join("?" * len(dup_ids))), (*dup_ids, keep_id))
        # Supprimer les doublons
        conn.execute("DELETE FROM spools WHERE id IN ({})".format(
            ",".join("?" * len(dup_ids))), dup_ids)
    if dupes:
        conn.commit()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS spools (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                tray_uuid      TEXT UNIQUE,
                tag_uid        TEXT,
                name           TEXT NOT NULL,
                brand          TEXT,
                tray_type      TEXT,
                sub_brands     TEXT,
                color_name     TEXT,
                color_hex      TEXT,
                filament_code  TEXT,
                initial_weight INTEGER DEFAULT 1000,
                initial_remain INTEGER DEFAULT 100,
                price_per_kg   REAL,
                status         TEXT DEFAULT 'active',
                created_at     TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS consumption_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                spool_id    INTEGER REFERENCES spools(id) ON DELETE CASCADE,
                slot_index  INTEGER,
                remain_pct  INTEGER,
                logged_at   TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS ams_state (
                slot_index  INTEGER PRIMARY KEY,
                tray_uuid   TEXT,
                tag_uid     TEXT,
                remain_pct  INTEGER,
                updated_at  TEXT DEFAULT (datetime('now'))
            );

        """)
        _migrate(conn)
