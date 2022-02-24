import asyncio
import multiprocessing
import sys
import time
import unicodedata
from pathlib import Path
from pprint import pprint
from multiprocessing import current_process, Process
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
async def create_users(path):
    if test:
        await init_tortoise(host="localhost", password="postgres")
        # data_dir = Path("../users_datafiles/")
    else:
        await init_tortoise(host="localhost")
        # data_dir = Path("/var/lib/postgresql/TO_IMPORT")

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

    # for path in data_dir.iterdir():
    service = path.name

    logger.debug(f"{current_process()}| Парс {service}...")
    t = time.monotonic()
    users_data = parce_datafiles(path)
    t2 = time.monotonic() - t
    logger.debug(f"{current_process().name}| Запарсено данных {len(users_data)}. {t2} s")
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
        logger.debug(f"{current_process().name}| Создание объектов {pre}:{index}")
        users_objs = (HackedUser(email=x[0], password=x[1], service=service) for x in users_data[pre:index])

        # loop.create_task(bulk_users_create(users_objs))
        await bulk_users_create(users_objs)
        logger.debug(f"{current_process().name}| Объекты созданы {pre}:{index}")
        pre = index
    logger.debug(f"{current_process().name}| Создание оставшихся {pre}: {len(users_data)}")
    users_objs = (
        HackedUser(email=x[0], password=x[1], service=service) for x in users_data[pre: len(users_data)]
    )
    # loop.create_task(bulk_users_create(users_objs))

    await bulk_users_create(users_objs)
    # logger.debug(f"{current_process().name}| Созданы оставшиеся {pre}:{len(users_data)}")

    # users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in users_data]
    # for user in users_obj:
    #     logger.trace(f"{user.email}{user.password}")
    #     await user.save()

    # await HackedUser.bulk_create(
    #     users_obj,
    #     batch_size=100000,
    #
    # )
    logger.info(f"{current_process().name}| {service}| Все данные сохранены")


@logger.catch
def run_async_create_users(path):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(create_users(path))
    # asyncio.run(create_users(path))


@logger.catch
def run_process_create_users():
    # logger.info(f"{current_process().name}| Всего юзеров {len(await HackedUser.all())}")
    if test:
        data_dir = Path("../users_datafiles/")
    else:
        data_dir = Path("/var/lib/postgresql/TO_IMPORT")

    data_dirs = list(data_dir.iterdir())
    logger.info(f"Полученные папки {[d.name for d in data_dirs]}")
    # print(zip(data_dirs, ))
    # print(list(data_dirs))

    # for path in data_dirs:
    #     Process(target=run_async_create)
    #
    with multiprocessing.Pool(processes=3) as pool:
        results = pool.map(run_async_create_users, data_dirs)


test = False
batch_size = 500000


async def create_table():
    if test:
        await init_tortoise(host="localhost", password="postgres")
    else:
        await init_tortoise(host="95.105.113.65")

    # await Tortoise.generate_schemas()


if __name__ == '__main__':
    # run_async(create_users(test=True))
    # run_async(create_users(test=True))
    # asyncio.run(create_users())
    # asyncio.run(create_table())
    run_process_create_users()
