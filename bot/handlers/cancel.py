import asyncpg
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext, pool: asyncpg.Pool) -> None:
    current = await state.get_state()
    if current is None:
        await message.answer("Нет активного действия для отмены.")
        return

    await state.clear()
    await pool.execute(
        "DELETE FROM user_state WHERE user_id = $1",
        message.from_user.id,
    )
    await message.answer("Действие отменено.")
