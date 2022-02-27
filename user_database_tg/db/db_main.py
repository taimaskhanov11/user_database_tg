import argparse
import asyncio
import multiprocessing
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import current_process, Process
from pathlib import Path

from loguru import logger
from tortoise import Tortoise

from user_database_tg.db import models

from user_database_tg.config.config import TEST
from user_database_tg.db.utils.parsing_data import DataParser

BASE_DIR = Path(__file__).parent.parent.parent


async def init_tortoise(
        username="postgres",
        password="XJjKaDgB2n",
        host="95.105.113.65",
        port=5432,
        db_name="users_database"
):
    logger.debug(f"Инициализация BD {host}")
    await Tortoise.init(  # todo
        # _create_db=True,
        db_url=f'postgres://{username}:{password}@{host}:{port}/{db_name}',
        modules={'models': ['user_database_tg.db.models']}
    )
    await Tortoise.generate_schemas()


@logger.catch
async def create_users(path):
    if TEST:
        await init_tortoise(host="localhost", password="postgres")
    else:
        await init_tortoise(host="localhost")

    service = path.name

    logger.debug(f"{current_process()}| Парс {service}...")
    t = time.monotonic()
    errors = ""
    data_parser = DataParser(path)
    try:
        await data_parser.parce_datafiles()
    except Exception as e:
        logger.critical(e)
        # raise e
        errors += f"{current_process().name}|{service} Ошибка"
    t2 = time.monotonic() - t
    logger.info(
        f"{current_process().name}|{service}| Все данные сохранены {t2}s.Всего запарсено {data_parser.all_count} {errors}")


@logger.catch
def run_async_create_users(path):
    logger.info(f"Запуск процесса {current_process().name}")
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(create_users(path))
    asyncio.run(create_users(path))


@logger.catch
def run_process_create_users(processes=3):
    # logger.info(f"{current_process().name}| Всего юзеров {len(await HackedUser.all())}")
    if TEST:
        data_dir = Path("../temp/users_datafiles/")
    else:
        data_dir = Path("/var/lib/postgresql/TO_IMPORT")
    data_dirs = list(data_dir.iterdir())
    logger.info(f"Полученные папки {[d.name for d in data_dirs]}")

    # print(zip(data_dirs, ))
    # print(list(data_dirs))

    def custom_pull_run():
        prs = []
        for path in data_dirs:
            prs.append(Process(target=run_async_create_users, args=(path,)))
            if len(prs) >= processes:
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

    def custom_pull_run2():
        prs = [Process(target=run_async_create_users, args=(path,)) for path in data_dirs]
        start_prs = []
        while True:
            if len(start_prs) >= processes:
                for start_pr in start_prs:
                    if not start_pr.is_alive():
                        logger.warning(f"Завершение старого процесса {start_pr.name}")
                        start_prs.remove(start_pr)
                        try:
                            pr = prs.pop()
                            logger.success(f"Создание процесса {pr.name}. Оставшиеся {prs}.Запущенные {start_prs}")
                            pr.start()
                            start_prs.append(pr)
                        except IndexError as e:
                            pass
            else:
                if not prs:
                    if not start_prs:
                        logger.critical(f"Завершение хендлера процессов {prs=}|{start_prs=}")
                        break
                    else:
                        for start_pr in start_prs:
                            if not start_pr.is_alive():
                                logger.warning(f"Завершение старого процесса {start_pr.name}")
                                start_prs.remove(start_pr)

                        logger.info(f"Ожидание завершения {start_prs=}")

                else:
                    pr = prs.pop()
                    logger.success(f"Создание процесса {pr.name}. Оставшиеся {prs}.Запущенные {start_prs}")
                    pr.start()
                    start_prs.append(pr)
            time.sleep(5)

    def pool_run():
        # mp_context = multiprocessing.get_context('fork') if not test else None
        with multiprocessing.Pool(processes=processes) as pool:
            # results = pool.map(run_async_create_users, data_dirs)
            pool.map(run_async_create_users, data_dirs)
            pool.join()

    def executor_run():
        with ProcessPoolExecutor(
                max_workers=3,
                # mp_context=multiprocessing.get_context('fork')
        ) as executor:
            results = executor.map(run_async_create_users, data_dirs)

    # custom_pull_run()
    custom_pull_run2()
    # pool_run()
    # executor_run()


async def init_db():
    if TEST:
        await init_tortoise(host="localhost", password="postgres")
    else:
        await init_tortoise(host="95.105.113.65")
    logger.debug(f"База данных инициализирована")


async def create_table():
    if TEST:
        await init_tortoise(host="localhost", password="postgres")
    else:
        await init_tortoise(host="95.105.113.65")
        # await HackedUser.all().delete()
    await Tortoise.generate_schemas()


def parse_args():
    parser = argparse.ArgumentParser(description="Parse data in  DB")
    parser.add_argument("-T", "--is_test", type=bool, default=False, help="Run in test mode", required=False)
    parser.add_argument("-T", "--is_test", type=bool, default=False, help="Run in test mode", required=False)
    args = parser.parse_args()
    print(args)


def init_logging():
    logger.remove()
    logger.add(sink=sys.stderr, level='TRACE', enqueue=True, diagnose=True, )
    # logger.add(sink=Path(BASE_DIR, "logs/paylog.log"), level='TRACE', enqueue=True, encoding='utf-8', diagnose=True, )
    logger.add(
        sink=Path(BASE_DIR, "logs/database.log"),
        level='TRACE',
        enqueue=True,
        encoding='utf-8',
        diagnose=True,
        rotation="5MB",
        # compression="zip",
    )


async def dell_all():
    await init_db()
    for h in models.__all__:
        await getattr(models, h).all().delete()


if __name__ == '__main__':
    init_logging()
    # run_process_create_users(4)
    asyncio.run(create_table())

    # asyncio.run(create_users())
    # mp_context =
    # asyncio.run(dell_all())
