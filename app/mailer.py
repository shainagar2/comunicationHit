# app/mailer.py
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from app.config import get_settings

def send_reset_email(to_email: str, reset_token: str) -> None:
    
    cfg = get_settings()

    if not cfg.smtp_user or not cfg.smtp_pass:
        # אם חסר קונפיג – נוֹדיע אבל לא נפיל את השרת
        raise RuntimeError("SMTP credentials are missing. Check .env")

    subject = "Password Reset | Comunication_LTD"
    # אפשר גם HTML, כאן טקסט פשוט:
    body = (
        "היי,\n\n"
        "הנה קוד האיפוס שלך (Token):\n"
        f"{reset_token}\n\n"
        "אם לא ביקשת איפוס – אפשר להתעלם מהמייל.\n"
    )

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Comunication_LTD", cfg.mail_from or cfg.smtp_user))
    msg["To"] = to_email

    with smtplib.SMTP(cfg.smtp_server, cfg.smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(cfg.smtp_user, cfg.smtp_pass)
        server.send_message(msg)
