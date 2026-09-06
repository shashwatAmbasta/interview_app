import sqlite3

from app.core.security import hash_password


def find_user_by_email(connection: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return connection.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()


def find_user_by_id(connection: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return connection.execute("SELECT id, email, name FROM users WHERE id = ?", (user_id,)).fetchone()


def create_user(connection: sqlite3.Connection, email: str, name: str, password: str, created_at: str) -> sqlite3.Row:
    cursor = connection.execute(
        "INSERT INTO users(email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (email.lower(), name, hash_password(password), created_at),
    )
    connection.commit()
    return connection.execute("SELECT id, email, name FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
