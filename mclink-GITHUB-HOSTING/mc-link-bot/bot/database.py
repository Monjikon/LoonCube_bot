import sqlite3
import random
import string
from datetime import datetime, timedelta
from contextlib import contextmanager
from config import DATABASE_PATH, CODE_LENGTH, CODE_EXPIRE_MINUTES


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS linked_accounts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                minecraft_uuid TEXT NOT NULL UNIQUE,
                minecraft_nick TEXT NOT NULL,
                platform    TEXT NOT NULL CHECK(platform IN ('telegram','vk')),
                user_id     TEXT NOT NULL,
                linked_at   TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pending_codes (
                code            TEXT PRIMARY KEY,
                minecraft_uuid  TEXT NOT NULL,
                minecraft_nick  TEXT NOT NULL,
                created_at      TEXT NOT NULL,
                expires_at      TEXT NOT NULL
            );
        """)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── коды привязки ────────────────────────────────────────────────────────────

def generate_code(minecraft_uuid: str, minecraft_nick: str) -> str:
    """Генерирует код для игрока и сохраняет его в БД."""
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=CODE_LENGTH))
    now = datetime.utcnow()
    expires = now + timedelta(minutes=CODE_EXPIRE_MINUTES)

    with get_conn() as conn:
        # удаляем старые коды этого игрока
        conn.execute("DELETE FROM pending_codes WHERE minecraft_uuid = ?", (minecraft_uuid,))
        conn.execute(
            "INSERT INTO pending_codes VALUES (?, ?, ?, ?, ?)",
            (code, minecraft_uuid, minecraft_nick, now.isoformat(), expires.isoformat()),
        )
    return code


def consume_code(code: str):
    """
    Проверяет код. Возвращает (minecraft_uuid, minecraft_nick) или None.
    Удаляет код после успешной проверки.
    """
    code = code.strip().upper()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM pending_codes WHERE code = ?", (code,)
        ).fetchone()
        if not row:
            return None
        if datetime.utcnow() > datetime.fromisoformat(row["expires_at"]):
            conn.execute("DELETE FROM pending_codes WHERE code = ?", (code,))
            return None
        conn.execute("DELETE FROM pending_codes WHERE code = ?", (code,))
        return row["minecraft_uuid"], row["minecraft_nick"]


# ── привязка аккаунтов ───────────────────────────────────────────────────────

def link_account(minecraft_uuid: str, minecraft_nick: str, platform: str, user_id: str) -> bool:
    """
    Привязывает аккаунт. Возвращает True при успехе.
    Если аккаунт уже привязан — перезаписывает.
    """
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO linked_accounts
               (minecraft_uuid, minecraft_nick, platform, user_id, linked_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(minecraft_uuid) DO UPDATE SET
                   minecraft_nick=excluded.minecraft_nick,
                   platform=excluded.platform,
                   user_id=excluded.user_id,
                   linked_at=excluded.linked_at""",
            (minecraft_uuid, minecraft_nick, platform, str(user_id), now),
        )
    return True


def unlink_account_by_user(platform: str, user_id: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM linked_accounts WHERE platform=? AND user_id=?",
            (platform, str(user_id)),
        )
        return cur.rowcount > 0


def get_link_by_user(platform: str, user_id: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM linked_accounts WHERE platform=? AND user_id=?",
            (platform, str(user_id)),
        ).fetchone()


def get_link_by_uuid(minecraft_uuid: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM linked_accounts WHERE minecraft_uuid=?",
            (minecraft_uuid,),
        ).fetchone()


def get_link_by_nick(minecraft_nick: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM linked_accounts WHERE LOWER(minecraft_nick)=LOWER(?)",
            (minecraft_nick,),
        ).fetchone()
