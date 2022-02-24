import asyncio
import sys
import time
import unicodedata
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
    batch_size = 500000
    logger.info(f"Всего юзеров {len(await HackedUser.all())}")

    @logger.catch
    async def bulk_users_create(objs):
        try:
            # asyncio.create_task(HackedUser.bulk_create(
            #     objs,
            #     batch_size=batch_size,
            # ))

            await HackedUser.bulk_create(
                objs,
                batch_size=batch_size,
            )
        except Exception as e:
            with open("incorrect_data/trash.txt", "w", encoding="utf-8") as f:
                logger.debug("Запись в файл")
                f.writelines(map(lambda x: f"{x[0]}:{x[1]}\n", users_data[pre:index]))
            raise e

    # for path in Path("../test2/").iterdir():
    # for path in Path("../test_users_datafiles/").iterdir():
    for path in Path("/var/lib/postgresql/TO_IMPORT").iterdir():
        # for path in Path("../users_datafiles/").iterdir():
        service = path.name

        logger.debug(f"Парс {service}...")
        t = time.monotonic()
        users_data = parce_datafiles(path)
        t2 = time.monotonic() - t
        logger.debug(f"Запарсено данных {len(users_data)}. {t2} s")
        # for data in users_data:
        # pprint(users_data)

        # for a, b in users_data:
        #     if a == "almacenestitch@hotmail.com" and b.startswith("ì"):
        #         print(a, b)
        #         print(b.replace("\x00", " "))
        # exit()

        pre = 0
        for index in range(0, len(users_data), batch_size):
            # for index in range(0, len(users_data), 10):
            # print(pre, users_data)
            logger.debug(f"Создание объектов {pre}:{index}")
            users_objs = (HackedUser(email=x[0], password=x[1], service=service) for x in users_data[pre:index])

            asyncio.create_task(bulk_users_create(users_objs))
            # await bulk_users_create(users_objs)
            logger.debug(f"Объекты созданы {pre}:{index}")
            pre = index
        logger.debug(f"Создание оставшихся {pre}: {len(users_data)}")
        users_objs = (
            HackedUser(email=x[0], password=x[1], service=service) for x in users_data[pre: len(users_data)]
        )
        asyncio.create_task(bulk_users_create(users_objs))

        # await bulk_users_create(users_objs)
        logger.debug(f"Созданы оставшиеся {pre}:{len(users_data)}")

        # users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in users_data]
        # for user in users_obj:
        #     logger.trace(f"{user.email}{user.password}")
        #     await user.save()

        # await HackedUser.bulk_create(
        #     users_obj,
        #     batch_size=100000,
        #
        # )
        logger.info(f"{service}| Все данные сохранены")


if __name__ == '__main__':
    run_async(create_users())
    # asyncio.run(create_users())
