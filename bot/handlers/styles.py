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
from bot.handlers.states import StyleStates

router = Router()


@router.message(Command("set_style"))
async def cmd_set_style(message: Message, pool: asyncpg.Pool) -> None:
    rows = await pool.fetch("SELECT id, text FROM styles ORDER BY id")
    # Truncate text to 50 characters in Python to avoid encoding issues
    rows = [{"id": row["id"], "text": row["text"][:50]} for row in rows]
    text = format_list(rows, "text")
    kb = build_view_keyboard("add_style", "delete_styles")
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "add_style")
async def cb_add_style(
    callback: CallbackQuery, state: FSMContext, pool: asyncpg.Pool,
) -> None:
    await callback.answer()
    await state.set_state(StyleStates.waiting_for_style)
    await callback.message.answer("Отправьте пример поста в вашем стиле:")


@router.callback_query(F.data == "delete_styles")
async def cb_delete_styles(callback: CallbackQuery, pool: asyncpg.Pool) -> None:
    await callback.answer()
    rows = await pool.fetch("SELECT id, text FROM styles ORDER BY id")
    if not rows:
        await callback.message.answer("Список пуст")
        return
    # Truncate text to 50 characters in Python to avoid encoding issues
    rows = [{"id": row["id"], "text": row["text"][:50]} for row in rows]
    kb = build_delete_keyboard(rows, "text", "del_st_")
    await callback.message.answer("Выберите стиль для удаления:", reply_markup=kb)


@router.callback_query(F.data.startswith("del_st_"))
async def cb_delete_style(callback: CallbackQuery, pool: asyncpg.Pool) -> None:
    await callback.answer()
    style_id = int(callback.data.removeprefix("del_st_"))
    await pool.execute("DELETE FROM styles WHERE id = $1", style_id)
    await callback.message.answer("Стиль удалён")


@router.message(StateFilter(StyleStates.waiting_for_style))
async def handle_style_input(
    message: Message, state: FSMContext, pool: asyncpg.Pool,
) -> None:
    await pool.execute("INSERT INTO styles (text) VALUES ($1)", message.text.strip())
    await state.clear()
    await message.answer("Стиль добавлен")
