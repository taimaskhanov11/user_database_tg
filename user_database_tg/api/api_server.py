import asyncio

from fastapi import FastAPI
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from user_database_tg.api.schema import Item, HackedUserPydanticSet, TestItem, TestHackedUser, TokenUser
from user_database_tg.api.utils import initialize
from user_database_tg.app.utils.data_search_helpers import get_hack_model

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


asyncio.create_task(initialize())
