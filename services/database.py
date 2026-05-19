import asyncpg
from config import settings

_pool: asyncpg.Pool = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.DATABASE_URL)
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                tg_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                funnel_day INTEGER DEFAULT 0,
                paid BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW(),
                paid_at TIMESTAMP
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                amount NUMERIC,
                currency TEXT,
                provider TEXT,
                payment_id TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)


async def add_user(tg_id: int, username: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (tg_id, username)
            VALUES ($1, $2)
            ON CONFLICT (tg_id) DO NOTHING
        """, tg_id, username)


async def get_user(tg_id: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE tg_id = $1", tg_id)
        return dict(row) if row else None


async def set_paid(tg_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users SET paid = TRUE, paid_at = NOW()
            WHERE tg_id = $1
        """, tg_id)


async def increment_funnel_day(tg_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users SET funnel_day = funnel_day + 1
            WHERE tg_id = $1
        """, tg_id)


async def get_unpaid_users_on_day(day: int) -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT tg_id FROM users
            WHERE funnel_day = $1 AND paid = FALSE
        """, day)
        return [r["tg_id"] for r in rows]


async def save_payment(user_id: int, amount, currency: str, provider: str, payment_id: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO payments (user_id, amount, currency, provider, payment_id)
            VALUES ($1, $2, $3, $4, $5)
        """, user_id, amount, currency, provider, payment_id)


async def get_stats() -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        paid = await conn.fetchval("SELECT COUNT(*) FROM users WHERE paid = TRUE")
        by_day = await conn.fetch("""
            SELECT funnel_day, COUNT(*) as cnt
            FROM users WHERE paid = FALSE
            GROUP BY funnel_day ORDER BY funnel_day
        """)
        return {
            "total": total,
            "paid": paid,
            "conversion": round(paid / total * 100, 1) if total else 0,
            "by_day": {r["funnel_day"]: r["cnt"] for r in by_day}
        }
