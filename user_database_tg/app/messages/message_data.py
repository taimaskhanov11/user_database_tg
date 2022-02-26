import asyncio
from typing import NamedTuple

from user_database_tg.db.db_main import init_db
from user_database_tg.db.models import DbMessage


class Translation(NamedTuple, ):
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
    go_payment: str

    reject_payment: str
    reject_payment_b: str


async def init_translations():
    await init_db()
    for trans_data in await DbMessage.all():
        trans = Translation(**dict(trans_data))
        print(trans)
        # print(dict(trans_data))


translations: [str, Translation] = {
}

if __name__ == '__main__':
    asyncio.run(init_translations())
