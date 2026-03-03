import asyncpg

from bot.config import config

pool: asyncpg.Pool | None = None


async def init_pool() -> asyncpg.Pool:
    global pool
    pool = await asyncpg.create_pool(
        host=config.db_host,
        port=config.db_port,
        database=config.db_name,
        user=config.db_user,
        password=config.db_password,
        min_size=2,
        max_size=10,
    )
    return pool


async def close_pool() -> None:
    global pool
    if pool:
        await pool.close()
        pool = None


def get_pool() -> asyncpg.Pool:
    if pool is None:
        raise RuntimeError("Database pool is not initialized")
    return pool
