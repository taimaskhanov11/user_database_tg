import asyncio

from pydantic import BaseModel

from user_database_tg.db.db_main import init_db
from user_database_tg.db.models import DbMessage


class Translation(BaseModel):
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
    wait_payment: str
    go_payment_b: str

    reject_payment: str
    reject_payment_b: str


async def init_translations():
    for trans_data in await DbMessage.all():
        translation = Translation(**dict(trans_data))
        translations[trans_data.language] = translation

translations: [str, Translation] = {
}

if __name__ == '__main__':
    asyncio.run(init_translations())
