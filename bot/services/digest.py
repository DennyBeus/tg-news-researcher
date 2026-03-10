import logging
import traceback
from datetime import datetime, timezone, timedelta

import asyncpg
from aiogram import Bot

from bot.config import config
from bot.services.openai_service import summarize_news

logger = logging.getLogger(__name__)

MSK = timezone(timedelta(hours=3))


async def notify_error(bot: Bot, job_name: str, exc: Exception) -> None:
    """Send a critical error notification to the admin chat."""
    tb = traceback.format_exc()
    text = (
        f"<b>Критическая ошибка: {job_name}</b>\n\n"
        f"{type(exc).__name__}: {exc}\n\n"
        f"<pre>{tb[-1000:]}</pre>"
    )
    try:
        await bot.send_message(config.chat_id, text)
    except Exception:
        logger.exception("Failed to send error notification to Telegram")


async def _build_and_send_digest(bot: Bot, pool: asyncpg.Pool, chat_id: int) -> None:
    """Fetch recent news, summarize and send digest to chat_id."""
    posts = await pool.fetch(
        "SELECT id, text, date, link, source_channel "
        "FROM news WHERE created_at > NOW() - INTERVAL '24 hours' "
        "ORDER BY date DESC"
    )

    if not posts:
        await bot.send_message(chat_id, "Нет новостей за последние 24 часа.")
        return

    posts_dicts = [dict(r) for r in posts]
    now_msk = datetime.now(MSK)
    for p in posts_dicts:
        if isinstance(p.get("date"), datetime):
            p["date"] = p["date"].strftime("%Y-%m-%d %H:%M:%S")

    summaries = await summarize_news(posts_dicts)

    date_str = now_msk.strftime("%d.%m.%Y")
    lines = [f"Дайджест за {date_str}\n"]
    for item in summaries:
        lines.append(
            f"id: {item.get('id', '?')}\n"
            f"{item.get('summary', '')}\n"
            f"link: {item.get('link', '')}\n"
        )

    message = "\n".join(lines)
    await bot.send_message(chat_id, message)
    logger.info("Digest sent for %s", date_str)


async def send_digest(bot: Bot, pool: asyncpg.Pool) -> None:
    """Check digest_time, summarize news and send digest to chat."""
    row = await pool.fetchrow(
        "SELECT value FROM settings WHERE key = 'digest_time'"
    )
    digest_time = row["value"] if row else "09:00"

    now_msk = datetime.now(MSK)
    current_time = now_msk.strftime("%H:%M")

    if current_time != digest_time:
        return

    await _build_and_send_digest(bot, pool, config.chat_id)


async def send_digest_now(bot: Bot, pool: asyncpg.Pool, chat_id: int) -> None:
    """Send digest immediately without time check (manual trigger)."""
    await _build_and_send_digest(bot, pool, chat_id)


