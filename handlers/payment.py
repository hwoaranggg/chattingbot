import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from services.payment_service import create_yukassa_payment, create_crypto_invoice, check_yukassa_payment
from services.database import set_paid, save_payment, get_user
from services.channel import grant_channel_access
from keyboards.payment import payment_keyboard, check_payment_keyboard

router = Router()
logger = logging.getLogger(__name__)


# ─── Выбор способа оплаты ─────────────────────────────────────────────────────

@router.callback_query(F.data == "pay_yukassa")
async def pay_yukassa(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await callback.answer()

    await callback.message.edit_text("⏳ Создаём счёт...")
    data = await create_yukassa_payment(tg_id)

    await callback.message.edit_text(
        f"💳 <b>Оплата картой РФ</b>\n\n"
        f"Нажми кнопку ниже, оплати и вернись сюда — нажми «Я оплатил».\n\n"
        f'<a href="{data["confirmation_url"]}">👉 Перейти к оплате</a>',
        reply_markup=check_payment_keyboard("yukassa", data["payment_id"]),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "pay_crypto")
async def pay_crypto(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await callback.answer()

    await callback.message.edit_text("⏳ Создаём инвойс...")
    data = await create_crypto_invoice(tg_id)

    await callback.message.edit_text(
        f"💰 <b>Оплата криптой (USDT)</b>\n\n"
        f"Нажми кнопку ниже, оплати и вернись — нажми «Я оплатил».\n\n"
        f'<a href="{data["pay_url"]}">👉 Перейти к оплате</a>',
        reply_markup=check_payment_keyboard("crypto", str(data["invoice_id"])),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_payment")
async def back_to_payment(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "👇 Выбери удобный способ оплаты:",
        reply_markup=payment_keyboard()
    )


# ─── Проверка оплаты ──────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("check_"))
async def check_payment(callback: CallbackQuery, bot: Bot):
    tg_id = callback.from_user.id
    await callback.answer("Проверяем...")

    parts = callback.data.split("_", 2)
    provider = parts[1]
    payment_id = parts[2]

    paid = False

    if provider == "yukassa":
        paid = await check_yukassa_payment(payment_id)
    elif provider == "crypto":
        paid = await check_crypto_invoice(payment_id, tg_id)

    if paid:
        await set_paid(tg_id)
        await save_payment(tg_id, None, "RUB" if provider == "yukassa" else "USDT", provider, payment_id)

        invite_link = await grant_channel_access(bot, tg_id)

        await callback.message.edit_text(
            f"🎉 <b>Оплата подтверждена!</b>\n\n"
            f"Твой доступ в закрытый канал:\n{invite_link}\n\n"
            f"⚠️ Ссылка одноразовая — используй сразу.",
            parse_mode="HTML"
        )
        logger.info(f"Оплата получена от {tg_id} через {provider}")
    else:
        await callback.message.answer(
            "❌ Оплата пока не найдена. Подожди пару минут и нажми «Я оплатил» снова.\n\n"
            "Если оплатил, но ошибка повторяется — напиши нам."
        )


async def check_crypto_invoice(invoice_id: str, tg_id: int) -> bool:
    """Проверяем статус инвойса в CryptoBot"""
    import aiohttp
    from config import settings

    headers = {"Crypto-Pay-API-Token": settings.CRYPTOBOT_TOKEN}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}",
            headers=headers
        ) as resp:
            data = await resp.json()
            items = data.get("result", {}).get("items", [])
            if items:
                return items[0].get("status") == "paid"
    return False
