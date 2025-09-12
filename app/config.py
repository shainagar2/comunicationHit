# app/config.py
import os
from dataclasses import dataclass
from functools import lru_cache

# אם אתה משתמש בקובץ .env בשורש – אפשר לטעון אותו כאן (לא חובה אם כבר טענת במקום אחר)
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    # אם dotenv לא מותקן/לא בשימוש – מתעלמים בשקט
    pass


@dataclass(frozen=True)
class Settings:
    # --- בסיס ---
    app_name: str = os.getenv("APP_NAME", "Comunication_LTD")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    db_connection_string: str = os.getenv("DB_CONN", "")

    # --- מדיניות סיסמאות (ניתן לשליטה דרך .env) ---
    # אורך מינימלי
    pwd_min_len: int = int(os.getenv("PWD_MIN_LEN", "10"))
    # חובה לכלול אות גדולה/קטנה/ספרה/תו מיוחד
    pwd_require_upper: bool = os.getenv("PWD_REQ_UPPER", "true").lower() == "true"
    pwd_require_lower: bool = os.getenv("PWD_REQ_LOWER", "true").lower() == "true"
    pwd_require_digit: bool = os.getenv("PWD_REQ_DIGIT", "true").lower() == "true"
    pwd_require_special: bool = os.getenv("PWD_REQ_SPECIAL", "true").lower() == "true"
    # היסטוריית סיסמאות – לא לאפשר חזרה על N האחרונות
    pwd_history_n: int = int(os.getenv("PWD_HISTORY_N", "5"))

    # --- התחברות (מניעת Brute-Force) ---
    login_max_attempts: int = int(os.getenv("LOGIN_MAX_ATTEMPTS", "3"))

    # --- מצב הדגמה לגרסה פגיעה/מאובטחת ---
    vuln_mode: bool = os.getenv("VULN_MODE", "false").lower() == "true"

    # --- (רשות) תצורות אימייל/שליחה של טוקן שחזור סיסמה בדמו ---
    mail_from: str = os.getenv("MAIL_FROM", "noreply@example.com")


@lru_cache
def get_settings() -> Settings:
    """
    נטען פעם אחת ונשתמש ב-Depends(get_settings) בכל מקום שצריך קונפיגורציה.
    """
    return Settings()
