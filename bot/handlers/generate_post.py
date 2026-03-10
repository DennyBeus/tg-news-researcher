import asyncpg
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.states import GeneratePostStates
from bot.services.openai_service import generate_post_text

router = Router()


@router.message(Command("generate_post"))
async def cmd_generate_post(message: Message, state: FSMContext, pool: asyncpg.Pool) -> None:
    await state.set_state(GeneratePostStates.waiting_for_post_ids)
    await message.answer(
        "Отправьте id постов из дайджеста через пробел (например: 1 2 3 5 12)"
    )


@router.message(StateFilter(GeneratePostStates.waiting_for_post_ids))
async def handle_post_ids_input(
    message: Message, state: FSMContext, pool: asyncpg.Pool,
) -> None:
    ids = []
    for token in message.text.split():
        try:
            val = int(token)
            if val > 0:
                ids.append(val)
        except ValueError:
            continue

    if not ids:
        await message.answer(
            "Не удалось распознать id постов. "
            "Отправьте числа через пробел (например: 1 2 3) или /cancel для отмены"
        )
        return

    posts = await pool.fetch(
        "SELECT id, text, link, source_channel FROM news WHERE id = ANY($1::int[])",
        ids,
    )
    if not posts:
        await message.answer(
            "Посты с указанными id не найдены. Попробуйте другие id или /cancel"
        )
        return

    styles_rows = await pool.fetch("SELECT text FROM styles")
    styles_texts = [r["text"] for r in styles_rows]
    news_texts = [dict(r) for r in posts]

    await message.answer("Генерирую пост...")

    result = await generate_post_text(news_texts, styles_texts)

    await state.clear()
    await message.answer(result)
