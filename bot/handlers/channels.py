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
from bot.handlers.states import ChannelStates

router = Router()


@router.message(Command("set_channels"))
async def cmd_set_channels(message: Message, pool: asyncpg.Pool) -> None:
    rows = await pool.fetch("SELECT id, url FROM channels ORDER BY id")
    text = format_list(rows, "url")
    kb = build_view_keyboard("add_channel", "delete_channels")
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "add_channel")
async def cb_add_channel(
    callback: CallbackQuery, state: FSMContext, pool: asyncpg.Pool,
) -> None:
    await callback.answer()
    await state.set_state(ChannelStates.waiting_for_channel)
    await callback.message.answer(
        "Отправьте URL канала (например: https://t.me/channel_name)"
    )


@router.callback_query(F.data == "delete_channels")
async def cb_delete_channels(callback: CallbackQuery, pool: asyncpg.Pool) -> None:
    await callback.answer()
    rows = await pool.fetch("SELECT id, url FROM channels ORDER BY id")
    if not rows:
        await callback.message.answer("Список пуст")
        return
    kb = build_delete_keyboard(rows, "url", "del_ch_")
    await callback.message.answer("Выберите канал для удаления:", reply_markup=kb)


@router.callback_query(F.data.startswith("del_ch_"))
async def cb_delete_channel(callback: CallbackQuery, pool: asyncpg.Pool) -> None:
    await callback.answer()
    channel_id = int(callback.data.removeprefix("del_ch_"))
    await pool.execute("DELETE FROM channels WHERE id = $1", channel_id)
    await callback.message.answer("Канал удалён")


@router.message(StateFilter(ChannelStates.waiting_for_channel))
async def handle_channel_input(
    message: Message, state: FSMContext, pool: asyncpg.Pool,
) -> None:
    url = message.text.strip()
    await pool.execute(
        "INSERT INTO channels (url) VALUES ($1) ON CONFLICT (url) DO NOTHING", url,
    )
    await state.clear()
    await message.answer("Канал добавлен")
