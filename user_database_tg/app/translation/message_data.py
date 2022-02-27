import asyncio
from pprint import pprint

from loguru import logger
from pydantic import BaseModel

from user_database_tg.db.db_main import init_db
from user_database_tg.db.models import DbMessage


class Translation(BaseModel):
    db_message: DbMessage

    # start
    start_message: str

    # menu
    profile: str
    description: str
    support: str
    subscribe: str

    # menu buttons
    profile_b: str
    description_b: str
    support_b: str
    subscribe_b: str

    # waiting for end search
    wait_search: str
    data_not_found: str

    # waiting for pay
    create_payment: str
    wait_payment: str
    go_payment_b: str

    reject_payment: str
    reject_payment_b: str

    class Config:
        arbitrary_types_allowed = True


async def init_translations():
    # await init_db()
    for db_message in await DbMessage.all():
        logger.trace(repr(dict(db_message)))
        translation = Translation(**dict(db_message), db_message=db_message)
        translations[db_message.language] = translation
    logger.debug("Перевод Инициализирован")


translations: [str, Translation] = {

}

if __name__ == '__main__':
    asyncio.run(init_translations())
    print(translations)
