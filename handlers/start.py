import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from services.database import add_user, get_user, increment_funnel_day
from services.funnel_content import FUNNEL_MESSAGES, FREE_ANSWERS
from keyboards.payment import payment_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    await add_user(tg_id, username)
    user = await get_user(tg_id)

    if user and user["paid"]:
        await message.answer("✅ У тебя уже есть доступ к мануалу. Проверь закрытый канал!")
        return

    first_msg = FUNNEL_MESSAGES[1]
    await message.answer(first_msg["text"])
    await increment_funnel_day(tg_id)

    logger.info(f"Новый пользователь: {tg_id} @{username}")


@router.message(Command("buy"))
async def cmd_buy(message: Message):
    tg_id = message.from_user.id
    user = await get_user(tg_id)

    if user and user["paid"]:
        await message.answer("✅ У тебя уже есть доступ! Проверь закрытый канал.")
        return

    await message.answer(
        "💥 <b>Мануал по чаттингу на OnlyFans</b>\n\n"
        "Всё что нужно чтобы начать зарабатывать с нуля.\n\n"
        "👇 Выбери способ оплаты:",
        reply_markup=payment_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text)
async def handle_free_text(message: Message):
    tg_id = message.from_user.id
    user = await get_user(tg_id)

    if not user:
        await message.answer("Напиши /start чтобы начать 👋")
        return

    if user["paid"]:
        await message.answer("✅ У тебя уже есть доступ к мануалу. Проверь закрытый канал!")
        return

    day = user["funnel_day"]
    response = FREE_ANSWERS.get(day, FREE_ANSWERS["default"])
    await message.answer(response)
