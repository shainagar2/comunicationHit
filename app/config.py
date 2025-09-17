# app/config.py
import os
from dataclasses import dataclass
from functools import lru_cache

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    pass


@dataclass(frozen=True)
class Settings:
 
    app_name: str = os.getenv("APP_NAME", "Comunication_LTD")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    db_connection_string: str = os.getenv("DB_CONN", "")

    pwd_min_len: int = int(os.getenv("PWD_MIN_LEN", "10"))
    pwd_require_upper: bool = os.getenv("PWD_REQ_UPPER", "true").lower() == "true"
    pwd_require_lower: bool = os.getenv("PWD_REQ_LOWER", "true").lower() == "true"
    pwd_require_digit: bool = os.getenv("PWD_REQ_DIGIT", "true").lower() == "true"
    pwd_require_special: bool = os.getenv("PWD_REQ_SPECIAL", "true").lower() == "true"
    pwd_history_n: int = int(os.getenv("PWD_HISTORY_N", "5"))
    login_max_attempts: int = int(os.getenv("LOGIN_MAX_ATTEMPTS", "3"))
    vuln_mode: bool = os.getenv("VULN_MODE", "false").lower() == "true"
  
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")
    mail_from: str = os.getenv("MAIL_FROM", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
