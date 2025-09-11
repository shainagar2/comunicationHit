from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

# הגדרות – שים לב לשם המשתנה: settings (לא setting)
settings = get_settings()

# מקור האמת למחרוזת חיבור: קודם מה-ENV ואם אין – מה-config
DB_CONN = os.getenv("DB_CONN", settings.db_connection_string)

# יוצר engine יחיד בלבד
engine = create_engine(DB_CONN, pool_pre_ping=True, future=True)

# Session manager
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Base למחלקות ORM
Base = declarative_base()

# תלות ל-API לקבלת session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# בדיקת חיבור מהירה
def test_connection():
    try:
        with engine.connect() as conn:
            val = conn.execute(text("SELECT 1")).scalar_one()
            print("Database connection OK:", val)
    except Exception as e:
        print("Database connection FAILED:", e)
