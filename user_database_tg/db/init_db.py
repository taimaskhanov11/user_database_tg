import sys
from pathlib import Path
from pprint import pprint

from loguru import logger
from tortoise import Tortoise, run_async

from user_database_tg.db.models import HackedUser
from user_database_tg.utils.parsing_data import parce_datafiles

BASE_DIR = Path(__file__).parent.parent.parent

logger.remove()
logger.add(sink=sys.stderr, level='TRACE', enqueue=True, diagnose=True, )
logger.add(sink=Path(BASE_DIR, "logs/paylog.log"), level='TRACE', enqueue=True, encoding='utf-8', diagnose=True, )


async def init_tortoise(
        username="postgres",
        password="XJjKaDgB2n",
        host="95.105.113.65",
        port=5432,
        db_name="users_database"
):
    await Tortoise.init(  # todo
        # _create_db=True,
        db_url=f'postgres://{username}:{password}@{host}:{port}/{db_name}',
        modules={'models': ['user_database_tg.db.models']}
    )
    await Tortoise.generate_schemas()


async def create_users_():
    # await init_tortoise()
    await init_tortoise(host="localhost", password="postgres")
    users_data = parce_datafiles("/var/lib/postgresql/TO_IMPORT")
    for service, data in users_data.items():
        users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in data]
        await HackedUser.bulk_create(
            users_obj
        )


@logger.catch
async def create_users():
    # await init_tortoise()
    # await init_tortoise(host="localhost", password="postgres")
    await init_tortoise(host="localhost")
    for path in Path("/var/lib/postgresql/TO_IMPORT").iterdir():
        # for path in Path("../users_datafiles/").iterdir():
        service = path.name

        logger.debug(f"Парс {service}...")
        users_data = parce_datafiles(path)
        logger.debug(f"Запарсено данных {len(users_data)}")
        # for data in users_data:
        # pprint(users_data)
        users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in users_data]

        # for user in users_obj:
        #     logger.trace(f"{user.email}{user.password}")
        #     await user.save()
        # HackedUser.save()

        await HackedUser.bulk_create(
            users_obj,
            batch_size=100000,

        )
        logger.info(f"{service}| Все данные сохранены")


if __name__ == '__main__':
    run_async(create_users())
    # asyncio.run(create_users())
