import re

import asyncpg
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.states import DigestTimeStates

router = Router()

TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


@router.message(Command("set_digest_time"))
async def cmd_set_digest_time(message: Message, state: FSMContext, pool: asyncpg.Pool) -> None:
    await state.set_state(DigestTimeStates.waiting_for_digest_time)
    await message.answer("Отправьте время в формате HH:MM (например: 09:00). Таймзона: МСК.")


@router.message(StateFilter(DigestTimeStates.waiting_for_digest_time))
async def handle_digest_time_input(
    message: Message, state: FSMContext, pool: asyncpg.Pool,
) -> None:
    text = message.text.strip()
    if not TIME_RE.match(text):
        await message.answer(
            "Неверный формат. Отправьте время в формате HH:MM (например: 09:00)"
        )
        return

    await pool.execute(
        "UPDATE settings SET value = $1 WHERE key = 'digest_time'", text,
    )
    await state.clear()
    await message.answer(f"Время дайджеста установлено: {text} МСК")
