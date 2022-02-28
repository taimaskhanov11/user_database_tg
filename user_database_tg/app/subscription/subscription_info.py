from loguru import logger
from pydantic import BaseModel

from user_database_tg.db.db_main import init_db
from user_database_tg.db.models import SubscriptionInfo


class SubscriptionPrices(BaseModel):  # legacy
    title: str
    days: int
    daily_limit: int
    price: int


SUBSCRIPTIONS_INFO: dict[int, SubscriptionInfo] = {}


async def init_subscriptions_info():
    # await init_db()
    for price in await SubscriptionInfo.all():
        SUBSCRIPTIONS_INFO[price.pk] = price
    logger.debug("Информация о подписках выгружена")
