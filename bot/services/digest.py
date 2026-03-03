import logging
from datetime import datetime, timezone, timedelta

import asyncpg
from aiogram import Bot

from bot.config import config
from bot.services.openai_service import summarize_news

logger = logging.getLogger(__name__)

MSK = timezone(timedelta(hours=3))


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

    posts = await pool.fetch(
        "SELECT id, text, date, link, source_channel "
        "FROM news WHERE created_at > NOW() - INTERVAL '24 hours' "
        "ORDER BY date DESC"
    )

    chat_id = config.chat_id

    if not posts:
        await bot.send_message(chat_id, "Нет новостей за последние 24 часа.")
        return

    posts_dicts = [dict(r) for r in posts]
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


async def check_errors(bot: Bot, pool: asyncpg.Pool) -> None:
    """Poll errors table and send unsent error notifications."""
    rows = await pool.fetch(
        "SELECT id, workflow_name, node_name, message, created_at "
        "FROM errors WHERE is_sent = FALSE ORDER BY id"
    )
    if not rows:
        return

    chat_id = config.chat_id
    for row in rows:
        text = (
            f"⚠️ Ошибка в workflow: {row['workflow_name']}\n"
            f"Нода: {row['node_name']}\n"
            f"Ошибка: {row['message']}\n"
            f"Время: {row['created_at'].strftime('%d.%m.%Y %H:%M')}"
        )
        await bot.send_message(chat_id, text)
        await pool.execute("UPDATE errors SET is_sent = TRUE WHERE id = $1", row["id"])

    logger.info("Sent %d error notification(s)", len(rows))
