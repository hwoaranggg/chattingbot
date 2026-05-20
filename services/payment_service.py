import uuid
import logging
import aiohttp
from config import settings

logger = logging.getLogger(__name__)


# ─── ЮKassa (карта) ───────────────────────────────────────────────────────────

async def create_yukassa_payment(tg_id: int) -> dict:
    """Оплата картой через ЮKassa"""
    idempotence_key = str(uuid.uuid4())
    payload = {
        "amount": {"value": str(settings.MANUAL_PRICE_RUB) + ".00", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://t.me/your_bot"},
        "capture": True,
        "description": f"Мануал по чаттингу | tg_id={tg_id}",
        "metadata": {"tg_id": str(tg_id)},
    }
    auth = aiohttp.BasicAuth(settings.YUKASSA_SHOP_ID, settings.YUKASSA_SECRET_KEY)
    headers = {"Idempotence-Key": idempotence_key, "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.yookassa.ru/v3/payments",
            json=payload, auth=auth, headers=headers
        ) as resp:
            data = await resp.json()
            return {
                "payment_id": data["id"],
                "confirmation_url": data["confirmation"]["confirmation_url"],
            }


# ─── ЮKassa (СБП) ─────────────────────────────────────────────────────────────

async def create_sbp_payment(tg_id: int) -> dict:
    """Оплата через СБП"""
    idempotence_key = str(uuid.uuid4())
    payload = {
        "amount": {"value": str(settings.MANUAL_PRICE_RUB) + ".00", "currency": "RUB"},
        "payment_method_data": {"type": "sbp"},
        "confirmation": {"type": "redirect", "return_url": "https://t.me/your_bot"},
        "capture": True,
        "description": f"Мануал по чаттингу | tg_id={tg_id}",
        "metadata": {"tg_id": str(tg_id)},
    }
    auth = aiohttp.BasicAuth(settings.YUKASSA_SHOP_ID, settings.YUKASSA_SECRET_KEY)
    headers = {"Idempotence-Key": idempotence_key, "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.yookassa.ru/v3/payments",
            json=payload, auth=auth, headers=headers
        ) as resp:
            data = await resp.json()
            return {
                "payment_id": data["id"],
                "confirmation_url": data["confirmation"]["confirmation_url"],
            }


async def check_yukassa_payment(payment_id: str) -> bool:
    """Проверяем статус платежа (работает и для карты и для СБП)"""
    auth = aiohttp.BasicAuth(settings.YUKASSA_SHOP_ID, settings.YUKASSA_SECRET_KEY)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.yookassa.ru/v3/payments/{payment_id}",
            auth=auth
        ) as resp:
            data = await resp.json()
            return data.get("status") == "succeeded"


# ─── CryptoBot ────────────────────────────────────────────────────────────────

async def create_crypto_invoice(tg_id: int) -> dict:
    """Создаём инвойс в CryptoBot"""
    headers = {"Crypto-Pay-API-Token": settings.CRYPTOBOT_TOKEN}
    payload = {
        "asset": "USDT",
        "amount": str(settings.MANUAL_PRICE_USDT),
        "description": f"Мануал по чаттингу | tg_id={tg_id}",
        "payload": str(tg_id),
        "allow_comments": False,
        "allow_anonymous": False,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://pay.crypt.bot/api/createInvoice",
            json=payload, headers=headers
        ) as resp:
            data = await resp.json()
            invoice = data["result"]
            return {
                "invoice_id": invoice["invoice_id"],
                "pay_url": invoice["pay_url"],
            }
