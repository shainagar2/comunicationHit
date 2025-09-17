# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.db import Base

# --- Users (משתמשים) ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    pswd_hash = Column(String(128), nullable=False)   # HMAC-SHA256 hex
    salt = Column(String(64), nullable=False)         # salt hex
    login_attempts = Column(Integer, nullable=False, default=0)
    is_locked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # קשרים
    customers = relationship("UserCustomer", back_populates="user", cascade="all, delete-orphan")
    password_history = relationship("PasswordHistory", back_populates="user", cascade="all, delete-orphan")
    resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")

# --- Customers (לקוחות) ---
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(120), nullable=False)
    sector = Column(String(80))
    package_name = Column(String(80))
    # לצורך הדגמת Stored XSS בגרסה ה"פרוצה"
    notes = Column(Text)

    owners = relationship("UserCustomer", back_populates="customer", cascade="all, delete-orphan")

# --- טבלת קישור user <-> customer ---
class UserCustomer(Base):
    __tablename__ = "user_customers"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True)

    user = relationship("User", back_populates="customers")
    customer = relationship("Customer", back_populates="owners")

# --- Password reset (שכחתי סיסמה; SHA-1) ---
class PasswordReset(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_sha1 = Column(String(40), unique=True, nullable=False)  # 40 hex chars (SHA-1)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="resets")

# --- היסטוריית סיסמאות (למדיניות "3 אחרונות") ---
class PasswordHistory(Base):
    __tablename__ = "password_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pswd_hash = Column(String(128), nullable=False)  # HMAC-SHA256 hex
    salt = Column(String(64), nullable=False)        # hex
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="password_history")

# --- דגלים (להדגמות SQLi/XSS במצב פרוץ) ---
class Flag(Base):
    __tablename__ = "flags"
    id = Column(Integer, primary_key=True)
    flag_value = Column(String(255), nullable=False)

# (רשות) Packages – אם תרצה לנרמל חבילות:
# class Package(Base):
#     __tablename__ = "packages"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(80), unique=True, nullable=False)
#     speed = Column(String(50))
#     price = Column(String(32))  # אפשר Decimal, השארתי פשוט
