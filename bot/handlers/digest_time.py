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
    await pool.execute(
        "INSERT INTO user_state (user_id, state, updated_at) "
        "VALUES ($1, 'waiting_for_digest_time', NOW()) "
        "ON CONFLICT (user_id) DO UPDATE SET state = 'waiting_for_digest_time', updated_at = NOW()",
        message.from_user.id,
    )
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
    await pool.execute("DELETE FROM user_state WHERE user_id = $1", message.from_user.id)
    await message.answer(f"Время дайджеста установлено: {text} МСК")
