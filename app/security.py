import os
import re
import hmac
import hashlib
from typing import Tuple, List
from app.config import get_settings

def gen_salt(n: int = 32) -> bytes:
    """יוצר salt אקראי חזק (בייטים)."""
    return os.urandom(n)


def hmac_sha256(password: str, salt: bytes) -> str:
    """מחזיר hex של HMAC-SHA256(salt, password)."""
    return hmac.new(salt, password.encode("utf-8"), hashlib.sha256).hexdigest()

def hash_password(password: str) -> Tuple[str, str]:
    """
    יוצר salt חדש ומחזיר (pswd_hash_hex, salt_hex).
    לשמירה בטבלת users: pswd_hash -> VARCHAR(128), salt -> VARCHAR(64).
    """
    salt = gen_salt()
    digest_hex = hmac_sha256(password, salt)
    return digest_hex, salt.hex()

def verify_password(password: str, salt_hex: str, expected_hex: str) -> bool:
    """אימות סיסמה באמצעות salt ששמור במסד ו־HMAC חדש; השוואה קבועת־זמן."""
    salt = bytes.fromhex(salt_hex)
    actual_hex = hmac_sha256(password, salt)
    return hmac.compare_digest(actual_hex, expected_hex)

# ---------------------------------
# 2) מדיניות סיסמאות מהקונפיגורציה
# ---------------------------------

_SPECIALS = r"!@#$%^&*()\-_=+\[\]{};:'\",.<>/?\\|`~"  # מותר להרחיב/לצמצם

def validate_password_policy(password: str) -> List[str]:
    """
    בודק את הסיסמה לפי מדיניות שמוגדרת ב-.env דרך Settings.
    מחזיר רשימת שגיאות (ריקה = תקין).
    """
    cfg = get_settings()
    errors: List[str] = []

    if len(password) < cfg.pwd_min_len:
        errors.append(f"סיסמה חייבת להיות באורך מינימלי של {cfg.pwd_min_len} תווים.")

    if cfg.pwd_require_upper and not re.search(r"[A-Z]", password):
        errors.append("סיסמה חייבת להכיל לפחות אות גדולה אחת (A-Z).")

    if cfg.pwd_require_lower and not re.search(r"[a-z]", password):
        errors.append("סיסמה חייבת להכיל לפחות אות קטנה אחת (a-z).")

    if cfg.pwd_require_digit and not re.search(r"\d", password):
        errors.append("סיסמה חייבת להכיל לפחות ספרה אחת (0-9).")

    if cfg.pwd_require_special and not re.search(rf"[{re.escape(_SPECIALS)}]", password):
        errors.append("סיסמה חייבת להכיל לפחות תו מיוחד אחד.")

    return errors

# ----------------------------------------------------
# 3) טוקן 'שכחתי סיסמה' (שומרים במסד רק את ה-SHA1)
# ----------------------------------------------------

def generate_reset_token_raw(n_bytes: int = 16) -> str:
    """
    יוצר טוקן גולמי להחזרה למשתמש (hex). את זה 'שולחים' במייל.
    בדמו אפשר להחזיר ב-API/לכתוב ל-log.
    """
    return os.urandom(n_bytes).hex()

def sha1_hex(s: str) -> str:
    """מחשב SHA-1 hex (לפי דרישת הקורס עבור טוקן reset)."""
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def make_reset_token_pair() -> Tuple[str, str]:
    """
    מייצר זוג (raw_token, token_sha1_hex):
    - raw_token: חוזר למשתמש (למייל/ל-API בדמו)
    - token_sha1_hex: זה מה שנשמר בטבלת password_resets.token_sha1
    """
    raw = generate_reset_token_raw()
    return raw, sha1_hex(raw)
