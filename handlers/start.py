import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from services.database import add_user, get_user
from keyboards.payment import payment_keyboard

router = Router()
logger = logging.getLogger(__name__)


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Купить мануал", callback_data="menu_buy")],
        [InlineKeyboardButton(text="📖 Что внутри мануала", callback_data="menu_content")],
        [InlineKeyboardButton(text="👤 Кто я такой", callback_data="menu_about")],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="menu_support")],
    ])


@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    await add_user(tg_id, username)

    await message.answer(
        "👋 Привет! Я помогу тебе разобраться с чаттингом на OnlyFans.\n\n"
        "Выбери что тебя интересует 👇",
        reply_markup=main_menu()
    )
    logger.info(f"Пользователь: {tg_id} @{username}")


# ─── Купить ───────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_buy")
async def menu_buy(callback: CallbackQuery):
    tg_id = callback.from_user.id
    user = await get_user(tg_id)
    await callback.answer()

    if user and user["paid"]:
        await callback.message.edit_text(
            "✅ У тебя уже есть доступ к мануалу. Проверь закрытый канал!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")]
            ])
        )
        return

    await callback.message.edit_text(
        f"💥 <b>Мануал по чаттингу на OnlyFans</b>\n\n"
        f"После оплаты ты сразу получаешь доступ в закрытый канал.\n\n"
        f"👇 Выбери способ оплаты:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            *payment_keyboard().inline_keyboard,
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")]
        ]),
        parse_mode="HTML"
    )


# ─── Что внутри ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_content")
async def menu_content(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📖 <b>Что внутри мануала:</b>\n\n"
        "✅ 30+ рабочих скриптов переписки\n"
        "✅ Как найти первую модель без опыта\n"
        "✅ Психология покупателя на OnlyFans\n"
        "✅ Техники повышения среднего чека\n"
        "✅ Как выйти на $1000+ в месяц по шагам\n"
        "✅ Разбор типичных ошибок новичков\n"
        "✅ Бесплатные обновления навсегда\n\n"
        "Всё что нужно чтобы начать зарабатывать с нуля 🔥",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Купить мануал", callback_data="menu_buy")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
        ]),
        parse_mode="HTML"
    )


# ─── Кто я ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_about")
async def menu_about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "👤 <b>Кто я такой:</b>\n\n"
        "Меня зовут Дмитрий.\n\n"
        "Я занимаюсь чаттингом на OnlyFans уже полгода "
        "и за это время заработал 8000$.\n\n"
        "Работал с несколькими моделями, знаю все подводные камни "
        "и собрал весь свой опыт в один мануал.\n\n"
        "[Добавь сюда своё фото или кейсы если есть]",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Купить мануал", callback_data="menu_buy")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
        ]),
        parse_mode="HTML"
    )


# ─── Поддержка ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_support")
async def menu_support(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💬 <b>Поддержка</b>\n\n"
        "Есть вопросы? Пиши напрямую:\n"
        "@reviemanager\n\n"
        "Отвечаю в течение нескольких часов.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_back")],
        ]),
        parse_mode="HTML"
    )


# ─── Назад в меню ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "👋 Привет! Я помогу тебе разобраться с чаттингом на OnlyFans.\n\n"
        "Выбери что тебя интересует 👇",
        reply_markup=main_menu()
    )
