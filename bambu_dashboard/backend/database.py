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
