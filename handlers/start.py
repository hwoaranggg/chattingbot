import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from services.database import add_user, get_user, increment_funnel_day
from services.funnel_content import FUNNEL_MESSAGES
from keyboards.payment import payment_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    await add_user(tg_id, username)
    user = await get_user(tg_id)

    # Если уже купил — напоминаем
    if user and user["paid"]:
        await message.answer("✅ У тебя уже есть доступ к мануалу. Проверь закрытый канал!")
        return

    # Первое сообщение воронки
    first_msg = FUNNEL_MESSAGES[1]
    await message.answer(first_msg["text"])
    await increment_funnel_day(tg_id)  # переводим на день 1 → ждём дня 2

    logger.info(f"Новый пользователь: {tg_id} @{username}")
