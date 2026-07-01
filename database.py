import sqlite3
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            points INTEGER NOT NULL DEFAULT 100,
            referral_code TEXT NOT NULL UNIQUE,
            referred_by INTEGER,
            is_admin INTEGER NOT NULL DEFAULT 0,
            bio TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            reward INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            referred_email TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    db.commit()

    cursor = db.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
    if cursor.fetchone()[0] == 0:
        db.execute(
            "INSERT INTO users (name, email, password_hash, points, referral_code, is_admin) VALUES (?, ?, ?, ?, ?, ?)"
            , ("Admin MoneyHub", "admin@moneyhub.local", "pbkdf2:sha256:260000$gGWb7KJb$Cd233f2a390ea7f60434e83d7979c6c00cac8df24f80af5ea16d1d87b3a2d9c3", 1000, "ADMIN100", 1)
        )
        db.commit()
