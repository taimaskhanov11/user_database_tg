from pathlib import Path

from loguru import logger

from user_database_tg.api.schema import auth_tokens
from user_database_tg.config.config import BASE_DIR
from user_database_tg.db.db_main import init_tortoise, init_logging
from user_database_tg.db.models import ApiSubscription


def init_loggings():
    logger.remove()
    logger.add(
        sink=Path(BASE_DIR, "logs/api.log"),
        level="TRACE",
        enqueue=True,
        encoding="utf-8",
        diagnose=True,
        rotation="5MB",
        # compression="zip",
    )


async def init_tokens():
    for sub in await ApiSubscription.all():
        if sub.days_duration:
            auth_tokens.append(sub.token)
    logger.info("Токены добавлены")


async def initialize():
    init_logging()
    await init_tortoise()
    await init_tokens()
    logger.info(f'API сервер запущен')
