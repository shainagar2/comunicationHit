# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from typing import List

from app.config import get_settings, Settings
from app.db import get_db
from app.models import (
    User, PasswordHistory, PasswordReset,
    Customer, UserCustomer
)
from app.security import (
    hash_password, verify_password, validate_password_policy, make_reset_token_pair
)
from app.mailer import send_reset_email   # ← חדש: שליחת מייל

router = APIRouter()

# ---------- Schemas ----------
class RegisterIn(BaseModel):
    email: EmailStr
    username: str
    password: str

class RegisterOut(BaseModel):
    id: int
    email: EmailStr
    username: str

class SignInIn(BaseModel):
    username: str
    password: str

class ChangePswdIn(BaseModel):
    username: str
    current_password: str
    new_password: str

class ForgotIn(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

class ResetIn(BaseModel):
    token: str
    new_password: str

class CustomerIn(BaseModel):
    full_name: str
    sector: str | None = None
    package: str | None = None
    notes: str | None = None

# ---------- Helpers ----------
def _password_reused(db: Session, user_id: int, candidate_password: str, take_last_n: int) -> bool:
    last: List[PasswordHistory] = (
        db.query(PasswordHistory)
          .filter(PasswordHistory.user_id == user_id)
          .order_by(desc(PasswordHistory.created_at))
          .limit(take_last_n)
          .all()
    )
    for hist in last:
        if verify_password(candidate_password, hist.salt, hist.pswd_hash):
            return True
    return False

def _append_password_history(db: Session, user_id: int, pswd_hash: str, salt_hex: str, keep_last_n: int):
    ph = PasswordHistory(user_id=user_id, pswd_hash=pswd_hash, salt=salt_hex)
    db.add(ph)
    db.flush()
    rows = (
        db.query(PasswordHistory)
          .filter(PasswordHistory.user_id == user_id)
          .order_by(desc(PasswordHistory.created_at))
          .all()
    )
    for i, row in enumerate(rows, start=1):
        if i > keep_last_n:
            db.delete(row)

def _require_mode(cfg: Settings, expected_vuln: bool):
    if cfg.vuln_mode != expected_vuln:
        raise HTTPException(status_code=404, detail="Not available in this mode")

# ---------- Register ----------
@router.post("/register", response_model=RegisterOut, tags=["auth"])
def register_user(data: RegisterIn, cfg: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    errors = validate_password_policy(data.password)
    if errors:
        raise HTTPException(status_code=400, detail={"policy_errors": errors})
    if db.query(User).filter((User.email == data.email) | (User.username == data.username)).first():
        raise HTTPException(status_code=409, detail="User with same email/username already exists")

    pswd_hash, salt_hex = hash_password(data.password)
    u = User(email=data.email, username=data.username, pswd_hash=pswd_hash, salt=salt_hex)
    db.add(u)
    db.flush()
    _append_password_history(db, u.id, pswd_hash, salt_hex, cfg.pwd_history_n)
    db.commit()
    db.refresh(u)
    return RegisterOut(id=u.id, email=u.email, username=u.username)

# ---------- Login + Lockout ----------
@router.post("/sign-in", tags=["auth"])
def sign_in(data: SignInIn, cfg: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.username == data.username).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if u.is_locked:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Account is locked")

    if not verify_password(data.password, u.salt, u.pswd_hash):
        u.login_attempts += 1
        if u.login_attempts >= cfg.login_max_attempts:
            u.is_locked = True
        db.commit()
        raise HTTPException(status_code=401, detail="Bad credentials")

    u.login_attempts = 0
    db.commit()
    return {"status": "OK", "user_id": u.id, "username": u.username}

# ---------- Change Password ----------
@router.post("/change-pswd", tags=["auth"])
def change_pswd(data: ChangePswdIn, cfg: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.username == data.username).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(data.current_password, u.salt, u.pswd_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    errors = validate_password_policy(data.new_password)
    if errors:
        raise HTTPException(status_code=400, detail={"policy_errors": errors})
    if _password_reused(db, u.id, data.new_password, cfg.pwd_history_n):
        raise HTTPException(status_code=400, detail=f"New password must not match the last {cfg.pwd_history_n} passwords")

    new_hash, new_salt = hash_password(data.new_password)
    u.pswd_hash = new_hash
    u.salt = new_salt
    _append_password_history(db, u.id, new_hash, new_salt, cfg.pwd_history_n)
    db.commit()
    return {"status": "OK"}

# ---------- Forgot Password (שליחת מייל אמיתית) ----------
@router.post("/forgot-password", tags=["auth"])
def forgot_password(data: ForgotIn, db: Session = Depends(get_db)):
    # אחד מהשדות חובה: username או email
    if not data.username and not data.email:
        raise HTTPException(status_code=400, detail="Provide username or email")

    q = db.query(User)
    if data.username:
        q = q.filter(User.username == data.username)
    if data.email:
        q = q.filter(User.email == data.email)

    u = q.first()
    if not u:
        # בפרודקשן נהוג להחזיר 200 כדי לא לחשוף קיום משתמש; בדמו נשאיר 404
        raise HTTPException(status_code=404, detail="User not found")

    # יצירת זוג (raw token, sha1(token))
    raw, sha1h = make_reset_token_pair()

    # מוחקים טוקנים ישנים ומשאירים אחד פעיל
    db.query(PasswordReset).filter(PasswordReset.user_id == u.id).delete()

    # שומרים ב-DB רק SHA-1
    db.add(PasswordReset(user_id=u.id, token_sha1=sha1h))
    db.commit()

    # שליחת מייל אמיתית למשתמש עם הטוקן הגלמי
    try:
        send_reset_email(u.email, raw)
    except Exception as e:
        # כדי לא "לשרוף" מידע ניתן להחזיר 200; כאן נחזיר שגיאה לדיבוג
        raise HTTPException(status_code=500, detail=f"Email send failed: {e}")

    return {"status": "OK", "message": "Reset token sent to email"}

# ---------- Reset Password ----------
@router.post("/reset-password", tags=["auth"])
def reset_password(data: ResetIn, cfg: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    if not data.token or not data.new_password:
        raise HTTPException(status_code=400, detail="Token and new_password are required")

    import hashlib
    sha1h = hashlib.sha1(data.token.encode("utf-8")).hexdigest()
    pr = db.query(PasswordReset).filter(PasswordReset.token_sha1 == sha1h).first()
    if not pr:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    u = db.query(User).filter(User.id == pr.user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    errors = validate_password_policy(data.new_password)
    if errors:
        raise HTTPException(status_code=400, detail={"policy_errors": errors})
    if _password_reused(db, u.id, data.new_password, cfg.pwd_history_n):
        raise HTTPException(status_code=400, detail=f"New password must not match the last {cfg.pwd_history_n} passwords")

    new_hash, new_salt = hash_password(data.new_password)
    u.pswd_hash = new_hash
    u.salt = new_salt
    _append_password_history(db, u.id, new_hash, new_salt, cfg.pwd_history_n)

    db.delete(pr)
    db.commit()
    return {"status": "OK"}

# ---------- Customers: create + list ----------
@router.post("/create_record", status_code=status.HTTP_201_CREATED, tags=["records"])
def create_customer(payload: CustomerIn, db: Session = Depends(get_db),
                    user_id: int = Query(1, description="Temp: ID of current user")):
    c = Customer(full_name=payload.full_name, sector=payload.sector,
                 package_name=payload.package, notes=payload.notes)
    db.add(c)
    db.flush()
    db.add(UserCustomer(user_id=user_id, customer_id=c.id))
    db.commit()
    return {"id": c.id}

@router.get("/get-customers", tags=["records"])
def get_customers(
    db: Session = Depends(get_db),
    user_id: int = Query(1, description="Temp: ID of current user"),
    q: str | None = Query(None, description="optional name filter")
):
    qset = (
        db.query(Customer)
          .join(UserCustomer, Customer.id == UserCustomer.customer_id)
          .filter(UserCustomer.user_id == user_id)
    )
    if q:
        qset = qset.filter(Customer.full_name.ilike(f"%{q}%"))

    rows = qset.order_by(Customer.id.desc()).all()
    return [
        {"id": r.id, "full_name": r.full_name, "sector": r.sector, "package": r.package_name, "notes": r.notes}
        for r in rows
    ]

# -----------------------------
#   VULN / SECURE דוגמאות
# -----------------------------
@router.get("/vuln/flags", tags=["vuln"])
def get_flag_vuln(id: str = Query("1"), cfg: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    """⚠️ פרוץ: SQLi ע"י חיבור מחרוזת. נסה: /vuln/flags?id=0 OR 1=1"""
    _require_mode(cfg, expected_vuln=True)
    sql = text(f"SELECT flag_value FROM flags WHERE id = {id} LIMIT 1")  # פגיע
    row = db.execute(sql).fetchone()
    return {"flag": row[0] if row else None}

@router.get("/secure/flags", tags=["secure"])
def get_flag_secure(id: int = Query(..., ge=1), cfg: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    """✅ מאובטח: שימוש בפרמטרים – אין הזרקה."""
    _require_mode(cfg, expected_vuln=False)
    row = db.execute(text("SELECT flag_value FROM flags WHERE id = :id"), {"id": id}).fetchone()
    return {"flag": row[0] if row else None}

@router.get("/vuln/customers/list_html", response_class=HTMLResponse, tags=["vuln"])
def list_customers_html_vuln(cfg: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    """⚠️ פרוץ: מחזיר HTML לא מקודד – <script> ב-notes ירוץ בדפדפן."""
    _require_mode(cfg, expected_vuln=True)
    rows = db.execute(text("SELECT full_name, notes FROM customers ORDER BY id DESC LIMIT 50")).fetchall()
    html = "<h3>Customers (VULN)</h3><ul>"
    for name, notes in rows:
        html += f"<li><b>{name}</b> — notes: {notes or ''}</li>"
    html += "</ul>"
    return html

@router.get("/secure/customers", tags=["secure"])
def list_customers_secure(cfg: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    """✅ מאובטח: מחזיר JSON בלבד (לקודד בצד הלקוח)."""
    _require_mode(cfg, expected_vuln=False)
    rows = db.execute(text("SELECT id, full_name, sector, package_name, notes FROM customers ORDER BY id DESC LIMIT 50")).fetchall()
    return [
        {"id": r[0], "full_name": r[1], "sector": r[2], "package": r[3], "notes": r[4]}
        for r in rows
    ]
