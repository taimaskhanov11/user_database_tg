import aiohttp
from loguru import logger

from user_database_tg.db.models import DbUser


async def send_decrypt_hash_request(db_user: DbUser, hashs: list[dict]) -> str:
    url = "http://localhost:8001/api/v1/hash"
    async with aiohttp.ClientSession() as session:
        # logger.info(db_user.trans_user_data)
        user_data = {
            "user_id": db_user.user_id,
            "username": db_user.username,
            "locale": db_user.language
        }
        logger.info(hashs)
        async with session.get(url, json={"user": user_data, "hashs": hashs}) as res:
            logger.info(await res.text())
            result = await res.json()
            return result


async def update_hash_requests(db_user: DbUser, month: int):
    url = "http://localhost:8001/api/v1/limit"
    data = {
        "trans_user": {"user_id": db_user.user_id,
                       "username": db_user.username,
                       "locale": db_user.language},
        "month": month,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as res:
            result = await res.json()
            return result
