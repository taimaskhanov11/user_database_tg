import asyncio
import sys
import time
from multiprocessing import current_process, Process
from pathlib import Path

from loguru import logger
from tortoise import Tortoise

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
    else:
        await init_tortoise(host="localhost")

    service = path.name

    logger.debug(f"{current_process()}| Парс {service}...")
    t = time.monotonic()
    count = await parce_datafiles(path, batch_size)
    t2 = time.monotonic() - t
    logger.info(f"{current_process().name}|{service}| Все данные сохранены {t2}s.Всего запарсено {count}")


@logger.catch
def run_async_create_users(path):
    logger.info(f"Запуск процесса {current_process().name}")
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(create_users(path))
    asyncio.run(create_users(path))


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
    prs = []
    for path in data_dirs:
        prs.append(Process(target=run_async_create_users, args=(path,)))
        if len(prs) >= 3:
            for p in prs:
                p.start()
            for p in prs:
                p.join()
            prs = []
    if prs:
        for p in prs:
            p.start()
        for p in prs:
            p.join()
        prs = []
    # mp_context = multiprocessing.get_context('fork') if not test else None
    # with multiprocessing.Pool(processes=3) as pool:
    #     results = pool.map(run_async_create_users, data_dirs)

    # with ProcessPoolExecutor(max_workers=3,
    #                          mp_context=mp_context) as executor:
    #     results = executor.map(run_async_create_users, data_dirs)
    # results = [executor.submit(run_async_create_users, path) for path in data_dirs]


test = False
batch_size = 500000


async def create_table():
    if test:
        await init_tortoise(host="localhost", password="postgres")
    else:
        await init_tortoise(host="95.105.113.65")
        await HackedUser.all().delete()
    # await Tortoise.generate_schemas()

async def chill():
    if test:
        await init_tortoise(host="localhost", password="postgres")
    else:
        await init_tortoise(host="95.105.113.65")


if __name__ == '__main__':
    # run_async(create_users(test=True))
    # run_async(create_users(test=True))
    # asyncio.run(create_users())
    # mp_context =
    run_process_create_users()
    # asyncio.run(create_table())
    # asyncio.run(chill())
