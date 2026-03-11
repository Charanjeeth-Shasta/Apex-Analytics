import sqlite3
import hashlib
import os
import re

DATABASE_PATH = os.path.join("database", "database.db")

# ─────────────────────────────────────────
# Validation rules (must match frontend)
# ─────────────────────────────────────────

USERNAME_MIN = 5
USERNAME_MAX = 20
PASSWORD_MIN = 8

def validate_username(username: str):
    """Returns (is_valid, error_message)."""
    if len(username) < USERNAME_MIN or len(username) > USERNAME_MAX:
        return False, f"Username must be {USERNAME_MIN}–{USERNAME_MAX} characters."
    if not re.match(r'^[A-Za-z0-9_]+$', username):
        return False, "Username may only contain letters, numbers, and underscores."
    return True, ""

def validate_password(password: str):
    """Returns (is_valid, error_message)."""
    if len(password) < PASSWORD_MIN:
        return False, f"Password must be at least {PASSWORD_MIN} characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password):
        return False, "Password must contain at least one special character."
    return True, ""

# ─────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────

def _get_conn():
    return sqlite3.connect(DATABASE_PATH)

def init_users_db():
    """Creates users table if it doesn't exist."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str):
    """
    Validates and creates a new user.
    Returns (success: bool, message: str).
    """
    ok, err = validate_username(username)
    if not ok:
        return False, err
    ok, err = validate_password(password)
    if not ok:
        return False, err

    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username.lower(), _hash(password))
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."
    finally:
        conn.close()

def verify_user(username: str, password: str):
    """
    Verifies credentials.
    Returns (success: bool, message: str).
    """
    conn = _get_conn()
    row = conn.execute(
        "SELECT password FROM users WHERE username = ?",
        (username.lower(),)
    ).fetchone()
    conn.close()

    if row is None:
        return False, "Username not found."
    if row[0] != _hash(password):
        return False, "Incorrect password."
    return True, "Login successful!"
