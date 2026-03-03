from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

WELCOME_TEXT = (
    "Привет! Я помогу собирать новости из Telegram-каналов.\n\n"
    "Команды:\n"
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
