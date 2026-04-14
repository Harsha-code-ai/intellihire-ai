"""
Database configuration — SQLAlchemy ORM.

Render's free tier uses an ephemeral filesystem.  The working directory may
reset between deploys, wiping a local SQLite file.  This module writes SQLite
to /tmp (survives restarts but not redeploys) by default, and strongly prefers
a DATABASE_URL pointing to a persistent PostgreSQL instance.

Priority:
  1. DATABASE_URL env var (PostgreSQL recommended for production)
  2. SQLITE_PATH env var  (custom SQLite file path, e.g. a Render disk mount)
  3. /tmp/intellihire.db  (last-resort ephemeral SQLite)
"""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
logger = logging.getLogger("intellihire.db")

# ─── URL resolution ───────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    # Heroku / Render sometimes gives postgres:// which SQLAlchemy 2.x rejects
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        logger.info("Rewrote postgres:// → postgresql://")
else:
    sqlite_path = os.getenv("SQLITE_PATH", "/tmp/intellihire.db")
    DATABASE_URL = f"sqlite:///{sqlite_path}"
    logger.warning(
        f"No DATABASE_URL set — using SQLite at {sqlite_path}.  "
        "Data will be lost on Render redeploy.  "
        "Set DATABASE_URL to a PostgreSQL connection string for persistence."
    )

logger.info(f"Database engine: {DATABASE_URL.split('@')[-1]}")  # hide credentials

# ─── Engine ───────────────────────────────────────────────────────────────────

_is_sqlite = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    # Keep a small pool; Render free tier has limited connections
    pool_pre_ping=True,           # detect stale connections
    pool_recycle=300,             # recycle every 5 min (avoids MySQL/PG timeouts)
    pool_size=5 if not _is_sqlite else 1,
    max_overflow=10 if not _is_sqlite else 0,
)

# Enable WAL mode for SQLite — better concurrent read performance
if _is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ─── Dependency ───────────────────────────────────────────────────────────────

def get_db():
    """FastAPI dependency: yields a DB session and ensures it is closed."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ─── Health check helper ──────────────────────────────────────────────────────

def ping_db() -> bool:
    """Return True if the database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB ping failed: {e}")
        return False