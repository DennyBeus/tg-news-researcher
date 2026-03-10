import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.db import get_pool
from bot.services.digest import check_errors, send_digest
from bot.services.pipeline import run_cleanup, run_pipeline

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


async def _pipeline_job() -> None:
    try:
        pool = get_pool()
        await run_pipeline(pool)
    except Exception:
        logger.exception("Pipeline job failed")


async def _cleanup_job() -> None:
    try:
        pool = get_pool()
        await run_cleanup(pool)
    except Exception:
        logger.exception("Cleanup job failed")


def start_scheduler(bot: Bot) -> None:
    global _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(_digest_job, "interval", minutes=1, args=[bot], id="digest")
    _scheduler.add_job(_errors_job, "interval", minutes=1, args=[bot], id="errors")
    _scheduler.add_job(_pipeline_job, "interval", hours=4, id="pipeline")
    _scheduler.add_job(_cleanup_job, "cron", hour=3, minute=0, id="cleanup")
    _scheduler.start()
    logger.info("Scheduler started (digest/errors: 1 min, pipeline: 4 h, cleanup: daily 03:00)")


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
