import asyncio
import json
import logging
import os
from datetime import datetime, timedelta

import asyncpg

from bot.services.openai_service import filter_by_interests

logger = logging.getLogger(__name__)

# Match the n8n workflow: parse interval (4h) + 1h buffer = 5h
_PARSE_WINDOW_HOURS = 5


def _get_parser_path() -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_root, "parser", "run.py")


async def run_pipeline(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        channels = await conn.fetch("SELECT url FROM channels")
        if not channels:
            logger.info("Pipeline: no channels configured, skipping")
            return

        interests = await conn.fetch("SELECT text FROM interests")

    channel_urls = [row["url"] for row in channels]
    interest_texts = [row["text"] for row in interests]

    start_dt = datetime.now() - timedelta(hours=_PARSE_WINDOW_HOURS)
    start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    parser_path = _get_parser_path()

    cmd = [
        "python", parser_path,
        "--stdout", "-f", "json", "-j", "-s", start_str,
        *channel_urls,
    ]

    logger.info("Pipeline: running parser for %d channel(s) since %s", len(channel_urls), start_str)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
    except Exception:
        logger.exception("Pipeline: failed to run parser")
        return

    if stderr:
        logger.debug("Parser stderr: %s", stderr.decode(errors="replace")[:500])

    raw = stdout.decode(errors="replace").strip()
    if not raw or raw == "[]":
        logger.info("Pipeline: parser returned no posts")
        return

    try:
        posts = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Pipeline: failed to parse parser output: %s", raw[:200])
        return

    if not posts:
        logger.info("Pipeline: no posts after parsing")
        return

    logger.info("Pipeline: got %d post(s), filtering by interests", len(posts))

    if interest_texts:
        posts = await filter_by_interests(posts, interest_texts)

    if not posts:
        logger.info("Pipeline: no posts matched interests")
        return

    logger.info("Pipeline: inserting %d post(s) into news", len(posts))
    await _insert_news(pool, posts)


async def _insert_news(pool: asyncpg.Pool, posts: list[dict]) -> None:
    async with pool.acquire() as conn:
        inserted = 0
        for p in posts:
            try:
                await conn.execute(
                    """
                    INSERT INTO news (text, date, views, reactions_count, link, source_channel)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (link) DO NOTHING
                    """,
                    p.get("text", ""),
                    p.get("date"),
                    p.get("views", 0),
                    p.get("reactions_count", 0),
                    p.get("link", ""),
                    p.get("source_channel", ""),
                )
                inserted += 1
            except Exception:
                logger.exception("Pipeline: failed to insert post %s", p.get("link"))
        logger.info("Pipeline: inserted %d post(s)", inserted)


async def run_cleanup(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM news WHERE date < NOW() - INTERVAL '1 month'")
    logger.info("Cleanup: %s", result)
