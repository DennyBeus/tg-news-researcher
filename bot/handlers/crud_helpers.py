"""Shared helpers for CRUD handlers (channels, interests, styles)."""

from typing import Sequence

import asyncpg
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_view_keyboard(
    add_callback: str,
    delete_callback: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить", callback_data=add_callback),
            InlineKeyboardButton(text="Удалить", callback_data=delete_callback),
        ]
    ])


def build_delete_keyboard(
    rows: Sequence[asyncpg.Record],
    display_field: str,
    callback_prefix: str,
) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"#{r['id']}: {r[display_field][:50]}",
            callback_data=f"{callback_prefix}{r['id']}",
        )]
        for r in rows
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_list(rows: Sequence[asyncpg.Record], display_field: str) -> str:
    if not rows:
        return "Список пуст."
    return "\n".join(f"#{r['id']}: {r[display_field]}" for r in rows)
