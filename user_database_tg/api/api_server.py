import asyncio
from datetime import datetime, timedelta

from fastapi import FastAPI
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from user_database_tg.api.schema import Item, HackedUserPydanticSet, TestItem, TestHackedUser, TokenUser, TransUser
from user_database_tg.api.utils import initialize
from user_database_tg.app.utils.data_search_helpers import get_hack_model
from user_database_tg.config.config import TZ
from user_database_tg.db.models import DbUser, Subscription

limiter = Limiter(key_func=get_remote_address, default_limits=["10/second"])
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@app.post("/api/v1/item/")
async def get_email_item(item: Item):
    """Main method"""
    logger.info(item)
    hack_model = await get_hack_model(item.email)
    items = await HackedUserPydanticSet.from_queryset(
        hack_model.filter(email=item.email).limit(item.limit)
    )
    return items


test_items = [TestHackedUser(email=f"email_{i}", password=f"password_{i}", service=f"service_{i}") for i in range(5)]


@app.post("/api/v1/test/item/")
async def read_item(item: TestItem):
    return test_items


@app.delete("/api/v1/token/")
async def delete_token(token_user: TokenUser):
    token_user.delete()
    logger.info("Токен удален")


@app.post("/api/v1/token/")
async def add_token(token_user: TokenUser):
    token_user.add()
    logger.info("Токен добавлен")


@app.post("/api/v1/sub/")
async def update_subscription(trans_user: TransUser):
    logger.trace(trans_user)
    logger.debug(f"Запрос на обновления количества запросов {trans_user.user_id}")
    db_user = await DbUser.get_or_new(trans_user.user_id, trans_user.username)
    if db_user.subscription.daily_limit is None:
        db_user.subscription.days_duration += trans_user.duration
        await db_user.subscription.save()
        logger.success(
            f"Успешна обновлена подписка для {trans_user.user_id}  на {trans_user.duration} "
            f"по партнерской программе с @Hash2PassBot")
    else:
        new_sub = await Subscription.create(
            title=f"Безлимит на {trans_user.duration // 30} месяц по партнерской программе с @Hash2PassBot",
            is_subscribe=True,
            is_paid=True,
            duration=datetime.now(TZ) + timedelta(trans_user.duration),
            days_duration=trans_user.duration,
            daily_limit=None,
            remaining_daily_limit=None,
        )

        old_sub = db_user.subscription
        db_user.subscription = new_sub

        await db_user.subscription.save()
        await db_user.save()
        await old_sub.delete()
        logger.success(
            f"Успешна создана новая подписка для {trans_user.user_id}  на {trans_user.duration} "
            f"по партнерской программе с @Hash2PassBot")


asyncio.create_task(initialize())
