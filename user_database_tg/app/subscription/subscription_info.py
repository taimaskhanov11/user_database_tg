from loguru import logger

from user_database_tg.db.models import SubscriptionInfo, ApiSubscriptionInfo

SUBSCRIPTIONS_INFO: dict[int, SubscriptionInfo] = {}
SUBSCRIPTIONS_INFO_API: dict[int, ApiSubscriptionInfo] = {}


async def init_subscriptions_info():
    # await init_db()
    for price in await SubscriptionInfo.all():
        SUBSCRIPTIONS_INFO[price.pk] = price

    for price in await ApiSubscriptionInfo.all():
        SUBSCRIPTIONS_INFO_API[price.pk] = price

    logger.debug("Информация о подписках выгружена")
