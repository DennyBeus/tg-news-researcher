import asyncpg
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.crud_helpers import (
    build_delete_keyboard,
    build_view_keyboard,
    format_list,
)
from bot.handlers.states import InterestStates

router = Router()


@router.message(Command("set_interests"))
async def cmd_set_interests(message: Message, pool: asyncpg.Pool) -> None:
    rows = await pool.fetch("SELECT id, text FROM interests ORDER BY id")
    text = format_list(rows, "text")
    kb = build_view_keyboard("add_interest", "delete_interests")
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "add_interest")
async def cb_add_interest(
    callback: CallbackQuery, state: FSMContext, pool: asyncpg.Pool,
) -> None:
    await callback.answer()
    await state.set_state(InterestStates.waiting_for_interest)
    await callback.message.answer("Отправьте текст интереса (ключевое слово или фразу):")


@router.callback_query(F.data == "delete_interests")
async def cb_delete_interests(callback: CallbackQuery, pool: asyncpg.Pool) -> None:
    await callback.answer()
    rows = await pool.fetch("SELECT id, text FROM interests ORDER BY id")
    if not rows:
        await callback.message.answer("Список пуст.")
        return
    kb = build_delete_keyboard(rows, "text", "del_int_")
    await callback.message.answer("Выберите интерес для удаления:", reply_markup=kb)


@router.callback_query(F.data.startswith("del_int_"))
async def cb_delete_interest(callback: CallbackQuery, pool: asyncpg.Pool) -> None:
    await callback.answer()
    interest_id = int(callback.data.removeprefix("del_int_"))
    await pool.execute("DELETE FROM interests WHERE id = $1", interest_id)
    await callback.message.answer("Интерес удалён.")


@router.message(StateFilter(InterestStates.waiting_for_interest))
async def handle_interest_input(
    message: Message, state: FSMContext, pool: asyncpg.Pool,
) -> None:
    await pool.execute("INSERT INTO interests (text) VALUES ($1)", message.text.strip())
    await state.clear()
    await message.answer("Интерес добавлен.")
