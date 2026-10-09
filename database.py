import aiosqlite
import secrets
from datetime import datetime, timedelta
from config import DB_PATH, SUBSCRIPTION_DAYS, ADMIN_IDS


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                xui_email TEXT UNIQUE,
                sub_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                notified_3d INTEGER DEFAULT 0,
                notified_0d INTEGER DEFAULT 0,
                invited_by INTEGER,
                invites_count INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS invite_links (
                token TEXT PRIMARY KEY,
                created_by INTEGER NOT NULL,
                friend_user_id INTEGER,
                friend_username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                is_used INTEGER DEFAULT 0,
                xui_email TEXT,
                sub_id TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS invites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inviter_id INTEGER NOT NULL,
                invited_user_id INTEGER,
                invited_username TEXT,
                invited_first_name TEXT,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


# ============================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()


async def get_user_by_username(username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ) as cursor:
            return await cursor.fetchone()


async def create_user_request(telegram_id: int, username: str, first_name: str,
                               xui_email: str, invited_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users
            (telegram_id, username, first_name, xui_email, status, invited_by)
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (telegram_id, username, first_name, xui_email, invited_by))
        await db.commit()


async def approve_user(telegram_id: int, sub_id: str, days: int = SUBSCRIPTION_DAYS):
    expires = datetime.now() + timedelta(days=days)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET status = 'active', sub_id = ?, expires_at = ?,
            notified_3d = 0, notified_0d = 0
            WHERE telegram_id = ?
        """, (sub_id, expires, telegram_id))
        await db.commit()


async def renew_user(telegram_id: int, new_expires=None, days: int = SUBSCRIPTION_DAYS):
    if new_expires is None:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT expires_at FROM users WHERE telegram_id = ?", (telegram_id,)
            ) as cursor:
                row = await cursor.fetchone()

            if row and row["expires_at"]:
                current = datetime.fromisoformat(row["expires_at"])
                new_expires = max(current, datetime.now()) + timedelta(days=days)
            else:
                new_expires = datetime.now() + timedelta(days=days)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET expires_at = ?, notified_3d = 0, notified_0d = 0
            WHERE telegram_id = ?
        """, (new_expires, telegram_id))
        await db.commit()
        return new_expires


async def get_expiring_users(days: int):
    target_date = (datetime.now() + timedelta(days=days)).date()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM users
            WHERE status = 'active'
            AND DATE(expires_at) = ?
            AND notified_3d = 0
        """, (target_date,)) as cursor:
            return await cursor.fetchall()


async def get_expired_today():
    today = datetime.now().date()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM users
            WHERE status = 'active'
            AND DATE(expires_at) = ?
            AND notified_0d = 0
        """, (today,)) as cursor:
            return await cursor.fetchall()


async def mark_notified(telegram_id: int, field: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field} = 1 WHERE telegram_id = ?", (telegram_id,))
        await db.commit()


async def increment_invites(inviter_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET invites_count = invites_count + 1
            WHERE telegram_id = ?
        """, (inviter_id,))
        await db.commit()


async def get_invites_count(telegram_id: int) -> int:
    user = await get_user(telegram_id)
    return user["invites_count"] if user else 0


async def delete_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        await db.commit()


async def get_inactive_users(days: int = 30) -> list:
    """Пользователи, у которых подписка истекла более N дней назад."""
    cutoff = datetime.now() - timedelta(days=days)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM users
            WHERE status = 'active'
            AND expires_at < ?
        """, (cutoff,)) as cur:
            return await cur.fetchall()


# ============================================================
# АДМИНЫ
# ============================================================

async def is_admin(telegram_id: int) -> bool:
    if telegram_id in ADMIN_IDS:
        return True
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,)) as cur:
            return await cur.fetchone() is not None


async def add_admin(telegram_id: int, username: str, added_by: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO admins (telegram_id, username, added_by)
            VALUES (?, ?, ?)
        """, (telegram_id, username, added_by))
        await db.commit()


async def remove_admin(username: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM admins WHERE username = ?", (username,))
        await db.commit()
        return cursor.rowcount > 0


async def get_all_admins() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT telegram_id, username FROM admins") as cur:
            return await cur.fetchall()


# ============================================================
# ОДНОРАЗОВЫЕ ССЫЛКИ-ПРИГЛАШЕНИЯ (для друзей без Telegram)
# ============================================================

async def create_invite_link(telegram_id: int, friend_user_id: int = None,
                              friend_username: str = None) -> str:
    """Создаёт одноразовую ссылку-приглашение.
    Возвращает уникальный токен."""
    token = secrets.token_urlsafe(24)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO invite_links
            (token, created_by, friend_user_id, friend_username)
            VALUES (?, ?, ?, ?)
        """, (token, telegram_id, friend_user_id, friend_username))
        await db.commit()

    return token


async def get_invite_link(token: str):
    """Получает приглашение по токену (только активное, до 7 дней)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM invite_links
            WHERE token = ? AND is_used = 0
            AND created_at > datetime('now', '-7 days')
        """, (token,)) as cur:
            return await cur.fetchone()


async def use_invite_link(token: str, xui_email: str, sub_id: str) -> bool:
    """Помечает ссылку использованной и сохраняет данные клиента."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            UPDATE invite_links
            SET is_used = 1, used_at = ?, xui_email = ?, sub_id = ?
            WHERE token = ? AND is_used = 0
        """, (datetime.now(), xui_email, sub_id, token))
        await db.commit()
        return cursor.rowcount > 0



# ============================================================
# УЧЁТ ПРИГЛАШЕНИЙ (для админ-статистики)
# ============================================================

async def add_invite(inviter_id: int, invited_user_id: int = None,
                      invited_username: str = None, invited_first_name: str = None,
                      invite_type: str = "ref"):
    """Записывает приглашение.
    invite_type: 'ref' (реферальная) или 'no_tg' (без Telegram).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO invites
            (inviter_id, invited_user_id, invited_username, invited_first_name, type)
            VALUES (?, ?, ?, ?, ?)
        """, (inviter_id, invited_user_id, invited_username, invited_first_name, invite_type))
        await db.commit()


async def get_global_invites_stats() -> dict:
    """Общая статистика по всем приглашениям."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            "SELECT COUNT(*) as c FROM invites WHERE type = 'ref'"
        ) as cur:
            ref_count = (await cur.fetchone())["c"]

        async with db.execute(
            "SELECT COUNT(*) as c FROM invites WHERE type = 'no_tg'"
        ) as cur:
            no_tg_count = (await cur.fetchone())["c"]

        return {
            "ref": ref_count,
            "no_tg": no_tg_count,
            "total": ref_count + no_tg_count
        }


async def get_top_inviters(limit: int = 5) -> list:
    """Топ пользователей по количеству приглашений."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT
                inviter_id,
                COUNT(CASE WHEN type = 'ref' THEN 1 END) as ref_count,
                COUNT(CASE WHEN type = 'no_tg' THEN 1 END) as no_tg_count,
                COUNT(*) as total
            FROM invites
            GROUP BY inviter_id
            ORDER BY total DESC
            LIMIT ?
        """, (limit,)) as cur:
            return await cur.fetchall()