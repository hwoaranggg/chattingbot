import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from services.database import get_stats
from keyboards.payment import payment_keyboard

router = Router()
logger = logging.getLogger(__name__)


def admin_only(message: Message) -> bool:
    return message.from_user.id == settings.ADMIN_ID


@router.message(Command("stats"), F.func(admin_only))
async def cmd_stats(message: Message):
    stats = await get_stats()
    by_day_text = "\n".join(
        f"  День {day}: {cnt} чел." for day, cnt in stats["by_day"].items()
    )
    await message.answer(
        f"📊 <b>Статистика воронки</b>\n\n"
        f"👥 Всего лидов: {stats['total']}\n"
        f"💰 Оплатили: {stats['paid']}\n"
        f"📈 Конверсия: {stats['conversion']}%\n\n"
        f"<b>Активные по дням:</b>\n{by_day_text or '—'}",
        parse_mode="HTML"
    )


@router.message(Command("broadcast"), F.func(admin_only))
async def cmd_broadcast(message: Message):
    """Ручная рассылка: /broadcast Текст сообщения"""
    text = message.text.removeprefix("/broadcast").strip()
    if not text:
        await message.answer("Использование: /broadcast Текст сообщения")
        return

    from services.database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        users = await conn.fetch("SELECT tg_id FROM users WHERE paid = FALSE")

    sent, failed = 0, 0
    for row in users:
        try:
            await message.bot.send_message(row["tg_id"], text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"✅ Отправлено: {sent}\n❌ Ошибок: {failed}")
