import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

logger = logging.getLogger(__name__)

# Try PostgreSQL first, fallback to SQLite if connection fails or not configured
db_url = settings.DATABASE_URL
engine = None

try:
    if "postgresql" in db_url:
        test_engine = create_engine(db_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        # Test connection
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        logger.info(f"Connected successfully to PostgreSQL database: {db_url}")
        print(f"[MedCode DB] Connected to PostgreSQL at {db_url}")
except Exception as e:
    logger.warning(f"PostgreSQL connection unavailable ({e}). Falling back to local SQLite database: {settings.SQLITE_FALLBACK_URL}")
    print(f"[MedCode DB] Notice: PostgreSQL unavailable ({e}). Running with SQLite fallback: {settings.SQLITE_FALLBACK_URL}")
    db_url = settings.SQLITE_FALLBACK_URL

if engine is None:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def ensure_schema_updated():
    """Ensures newly added columns and tables are present in existing database tables."""
    try:
        with engine.connect() as conn:
            if "sqlite" in db_url:
                cursor = conn.connection.cursor()
                
                # 1. Update sessions table
                cursor.execute("PRAGMA table_info(sessions);")
                columns = [row[1] for row in cursor.fetchall()]
                if columns:
                    if "zoom_meeting_url" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN zoom_meeting_url VARCHAR(500);")
                    if "zoom_meeting_id" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN zoom_meeting_id VARCHAR(100);")
                    if "teams_meeting_url" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN teams_meeting_url VARCHAR(500);")
                    if "teams_meeting_id" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN teams_meeting_id VARCHAR(100);")
                    if "consultation_source" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN consultation_source VARCHAR(50) DEFAULT 'Zoom';")
                    if "assigned_scrubber_id" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN assigned_scrubber_id VARCHAR(36);")
                    if "assigned_scrubber_name" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN assigned_scrubber_name VARCHAR(255);")
                    if "priority" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN priority VARCHAR(20) DEFAULT 'NORMAL';")
                    if "stage" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN stage VARCHAR(50) DEFAULT 'NEW';")
                    if "total_charges" not in columns:
                        cursor.execute("ALTER TABLE sessions ADD COLUMN total_charges FLOAT DEFAULT 320.00;")
                
                # 2. Update users table
                cursor.execute("PRAGMA table_info(users);")
                user_cols = [row[1] for row in cursor.fetchall()]
                if user_cols:
                    if "employee_id" not in user_cols:
                        cursor.execute("ALTER TABLE users ADD COLUMN employee_id VARCHAR(50) DEFAULT 'EMP-8021';")
                    if "organization" not in user_cols:
                        cursor.execute("ALTER TABLE users ADD COLUMN organization VARCHAR(255) DEFAULT 'Apex Health RCM Systems';")
                    if "department" not in user_cols:
                        cursor.execute("ALTER TABLE users ADD COLUMN department VARCHAR(100) DEFAULT 'Clinical Revenue & Coding';")
                    if "specialization" not in user_cols:
                        cursor.execute("ALTER TABLE users ADD COLUMN specialization VARCHAR(100) DEFAULT 'Outpatient & Inpatient Coding';")
                    if "phone" not in user_cols:
                        cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(50);")
                    if "last_login" not in user_cols:
                        cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME;")

                conn.connection.commit()
    except Exception as e:
        logger.warning(f"Schema update check skipped/failed: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
