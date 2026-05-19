import logging
from aiogram import Bot
from config import settings

logger = logging.getLogger(__name__)


async def grant_channel_access(bot: Bot, tg_id: int) -> str:
    """Создаём одноразовую инвайт-ссылку и возвращаем её"""
    link = await bot.create_chat_invite_link(
        chat_id=settings.PRIVATE_CHANNEL_ID,
        member_limit=1,  # одноразовая
        name=f"user_{tg_id}",
    )
    logger.info(f"Создана инвайт-ссылка для {tg_id}: {link.invite_link}")
    return link.invite_link
