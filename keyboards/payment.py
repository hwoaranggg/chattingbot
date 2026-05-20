from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import settings


def payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🏦 СБП — {settings.MANUAL_PRICE_RUB} ₽",
            callback_data="pay_sbp"
        )],
        [InlineKeyboardButton(
            text=f"💳 Карта РФ — {settings.MANUAL_PRICE_RUB} ₽",
            callback_data="pay_yukassa"
        )],
        [InlineKeyboardButton(
            text=f"💰 Крипта (USDT) — {settings.MANUAL_PRICE_USDT}$",
            callback_data="pay_crypto"
        )],
    ])


def check_payment_keyboard(provider: str, payment_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Я оплатил",
            callback_data=f"check_{provider}_{payment_id}"
        )],
        [InlineKeyboardButton(
            text="◀️ Другой способ оплаты",
            callback_data="back_to_payment"
        )],
    ])
