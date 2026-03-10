from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

WELCOME_TEXT = (
    "Привет! Я могу собирать новости из Telegram каналов, делать по ним дайджесты и генерировать посты в твоём стиле.\n\n"
    "Команды:\n"
    "/start — запуск бота\n"
    "/set_channels — управление каналами\n"
    "/set_interests — управление интересами\n"
    "/set_style — управление стилями постов\n"
    "/set_digest_time — время дайджеста\n"
    "/generate_post — генерация поста\n"
    "/cancel — отмена текущего действия"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT)
