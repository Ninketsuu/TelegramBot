import aiosqlite
from datetime import datetime

DB_PATH = "data/wellbeing.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS water_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount_ml INTEGER,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS sleep_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                hours REAL,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS steps_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                steps INTEGER,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS mood_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                score INTEGER,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                done INTEGER DEFAULT 0,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                created_at TEXT
            );
            """
        )
        await db.commit()

async def add_user_if_not_exists(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if not row:
            await db.execute(
                "INSERT INTO users (user_id, created_at) VALUES (?, ?)",
                (user_id, datetime.utcnow().isoformat()),
            )
            await db.commit()
        await cur.close()

async def add_water(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO water_logs (user_id, amount_ml, created_at) VALUES (?, ?, ?)",
            (user_id, amount, datetime.utcnow().isoformat()),
        )
        await db.commit()

async def add_sleep(user_id: int, hours: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO sleep_logs (user_id, hours, created_at) VALUES (?, ?, ?)",
            (user_id, hours, datetime.utcnow().isoformat()),
        )
        await db.commit()

async def add_steps(user_id: int, steps: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO steps_logs (user_id, steps, created_at) VALUES (?, ?, ?)",
            (user_id, steps, datetime.utcnow().isoformat()),
        )
        await db.commit()

async def log_mood(user_id: int, score: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO mood_logs (user_id, score, created_at) VALUES (?, ?, ?)",
            (user_id, score, datetime.utcnow().isoformat()),
        )
        await db.commit()

async def get_mood_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT AVG(score), COUNT(*) FROM mood_logs WHERE user_id = ?",
            (user_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        if row and row[1]:
            return float(row[0]), int(row[1])
        return None

async def add_task(user_id: int, title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO tasks (user_id, title, created_at) VALUES (?, ?, ?)",
            (user_id, title, datetime.utcnow().isoformat()),
        )
        await db.commit()

async def list_tasks(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT id, title, done FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return rows

async def complete_task(user_id: int, task_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "UPDATE tasks SET done = 1 WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        )
        await db.commit()
        return cur.rowcount > 0

async def add_achievement(user_id: int, title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO achievements (user_id, title, created_at) VALUES (?, ?, ?)",
            (user_id, title, datetime.utcnow().isoformat()),
        )
        await db.commit()

async def list_achievements(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT title, created_at FROM achievements WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return rows
