import logging

import asyncpg
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.digest import send_digest_now
from bot.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("run_digest"))
async def cmd_run_digest(message: Message, pool: asyncpg.Pool, bot: Bot) -> None:
    await message.answer("Запускаю парсер... Это может занять некоторое время.")

    try:
        await run_pipeline(pool)
    except Exception as e:
        logger.exception("run_digest: pipeline failed")
        await message.answer(f"Ошибка при парсинге: {e}")
        return

    await message.answer("Парсинг завершён. Формирую дайджест...")

    try:
        await send_digest_now(bot, pool, message.chat.id)
    except Exception as e:
        logger.exception("run_digest: digest failed")
        await message.answer(f"Ошибка при формировании дайджеста: {e}")
