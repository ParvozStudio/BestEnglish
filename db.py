import aiosqlite
from config import DB_PATH


class Database:
    def __init__(self):
        self.db_path = DB_PATH

    async def create_tables(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    phone TEXT,
                    child_name TEXT,
                    age INTEGER,
                    is_registered INTEGER DEFAULT 0,
                    is_blocked INTEGER DEFAULT 0,
                    joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_active TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    course_name TEXT NOT NULL,
                    subcourse TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_text TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
            # Eski bazalarda child_name ustuni bo'lmasligi mumkin — mavjud bo'lmasa qo'shamiz
            try:
                await db.execute("ALTER TABLE users ADD COLUMN child_name TEXT")
                await db.commit()
            except Exception:
                pass
            # To'lovlar bo'limi uchun ustunlar (eski bazalarda bo'lmasligi mumkin)
            try:
                await db.execute("ALTER TABLE users ADD COLUMN is_paying_student INTEGER DEFAULT 0")
                await db.commit()
            except Exception:
                pass
            try:
                await db.execute("ALTER TABLE users ADD COLUMN payment_status TEXT DEFAULT 'unpaid'")
                await db.commit()
            except Exception:
                pass

    # =================== USERS ===================

    async def add_user(self, telegram_id: int, username: str = None, full_name: str = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (telegram_id, username, full_name)
                VALUES (?, ?, ?)
            """, (telegram_id, username, full_name))
            await db.execute("""
                UPDATE users SET last_active = CURRENT_TIMESTAMP, username = ?, full_name = ?
                WHERE telegram_id = ?
            """, (username, full_name, telegram_id))
            await db.commit()

    async def update_user_registration(self, telegram_id: int, phone: str, age: int, child_name: str = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users SET phone = ?, age = ?, child_name = ?, is_registered = 1
                WHERE telegram_id = ?
            """, (phone, age, child_name, telegram_id))
            await db.commit()

    async def get_user(self, telegram_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users ORDER BY joined_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_registered_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE is_registered = 1 AND is_blocked = 0 ORDER BY joined_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_stats(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as c:
                total = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM users WHERE is_registered = 1") as c:
                registered = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM applications") as c:
                apps = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE last_active >= datetime('now', '-1 day')"
            ) as c:
                active_today = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM applications WHERE status = 'pending'"
            ) as c:
                pending_apps = (await c.fetchone())[0]
        return {
            "total": total,
            "registered": registered,
            "apps": apps,
            "active_today": active_today,
            "pending_apps": pending_apps
        }

    async def block_user(self, telegram_id: int, block: bool = True):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_blocked = ? WHERE telegram_id = ?",
                (1 if block else 0, telegram_id)
            )
            await db.commit()

    # =================== APPLICATIONS ===================

    async def add_application(self, user_id: int, course_name: str, subcourse: str = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO applications (user_id, course_name, subcourse)
                VALUES (?, ?, ?)
            """, (user_id, course_name, subcourse))
            await db.commit()

    async def get_user_applications(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_all_applications(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT a.*, u.full_name, u.username, u.phone, u.child_name
                FROM applications a
                LEFT JOIN users u ON a.user_id = u.telegram_id
                ORDER BY a.created_at DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def update_application_status(self, app_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE applications SET status = ? WHERE id = ?", (status, app_id)
            )
            await db.commit()

    # =================== TO'LOVLAR ===================

    async def mark_paying_student(self, telegram_id: int):
        """Ariza qabul qilinganda o'quvchi avtomatik 'to'lov qilmaganlar' ro'yxatiga qo'shiladi."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_paying_student = 1, payment_status = 'unpaid' WHERE telegram_id = ?",
                (telegram_id,)
            )
            await db.commit()

    async def get_unpaid_students(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE is_paying_student = 1 AND payment_status = 'unpaid' "
                "ORDER BY full_name"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_paid_students(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE is_paying_student = 1 AND payment_status = 'paid' "
                "ORDER BY full_name"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def set_payment_status(self, telegram_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET payment_status = ? WHERE telegram_id = ?",
                (status, telegram_id)
            )
            await db.commit()

    # =================== LOG ===================

    async def log_message(self, user_id: int, text: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages_log (user_id, message_text) VALUES (?, ?)",
                (user_id, text[:500] if text else "")
            )
            await db.commit()
