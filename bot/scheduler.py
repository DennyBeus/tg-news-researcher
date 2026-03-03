import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.db import get_pool
from bot.services.digest import check_errors, send_digest

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _digest_job(bot: Bot) -> None:
    try:
        pool = get_pool()
        await send_digest(bot, pool)
    except Exception:
        logger.exception("Digest job failed")


async def _errors_job(bot: Bot) -> None:
    try:
        pool = get_pool()
        await check_errors(bot, pool)
    except Exception:
        logger.exception("Error polling job failed")


def start_scheduler(bot: Bot) -> None:
    global _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(_digest_job, "interval", minutes=1, args=[bot], id="digest")
    _scheduler.add_job(_errors_job, "interval", minutes=1, args=[bot], id="errors")
    _scheduler.start()
    logger.info("Scheduler started (digest check every 1 min, error poll every 1 min)")


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
