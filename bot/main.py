import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.config import config
from bot.db import init_pool, close_pool
from bot.middlewares import DbMiddleware
from bot.scheduler import start_scheduler, shutdown_scheduler
from bot.handlers import (
    start,
    channels,
    interests,
    styles,
    digest_time,
    generate_post,
    cancel,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    await init_pool()
    start_scheduler(bot)
    logger.info("Bot started")


async def on_shutdown(bot: Bot) -> None:
    shutdown_scheduler()
    await close_pool()
    logger.info("Bot stopped")


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.message.middleware(DbMiddleware())
    dp.callback_query.middleware(DbMiddleware())

    dp.include_router(cancel.router)
    dp.include_router(start.router)
    dp.include_router(channels.router)
    dp.include_router(interests.router)
    dp.include_router(styles.router)
    dp.include_router(digest_time.router)
    dp.include_router(generate_post.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    return dp


async def main() -> None:
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
