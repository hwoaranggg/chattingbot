import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from services.database import get_unpaid_users_on_day, increment_funnel_day
from services.funnel_content import FUNNEL_MESSAGES
from keyboards.payment import payment_keyboard

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def send_funnel_messages(bot: Bot):
    """Каждый день отправляем следующее сообщение всем кто в воронке"""
    max_day = max(FUNNEL_MESSAGES.keys())

    for day in range(1, max_day + 1):
        users = await get_unpaid_users_on_day(day)
        msg = FUNNEL_MESSAGES.get(day)
        if not msg or not users:
            continue

        for tg_id in users:
            try:
                if msg["button"] == "buy":
                    await bot.send_message(tg_id, msg["text"], reply_markup=payment_keyboard())
                else:
                    await bot.send_message(tg_id, msg["text"])
                await increment_funnel_day(tg_id)
            except Exception as e:
                logger.warning(f"Не удалось отправить сообщение {tg_id}: {e}")


async def start_scheduler(bot: Bot):
    scheduler.add_job(
        send_funnel_messages,
        trigger="cron",
        hour=10,       # в 10:00 каждый день
        minute=0,
        args=[bot],
    )
    scheduler.start()
    logger.info("Планировщик прогрева запущен")
