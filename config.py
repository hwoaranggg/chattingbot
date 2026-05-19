from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int

    # База данных (Railway PostgreSQL)
    DATABASE_URL: str

    # ЮKassa
    YUKASSA_SHOP_ID: str
    YUKASSA_SECRET_KEY: str

    # CryptoBot
    CRYPTOBOT_TOKEN: str

    # Закрытый канал (ID с минусом, например -1001234567890)
    PRIVATE_CHANNEL_ID: int

    # Цена мануала
    MANUAL_PRICE_RUB: int = 2990
    MANUAL_PRICE_USDT: float = 29.0

    class Config:
        env_file = ".env"


settings = Settings()
