import argparse
import asyncio
import sys
from pathlib import Path

from loguru import logger
from tortoise import Tortoise

from user_database_tg.config.config import TEST, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_DB_NAME
from user_database_tg.db import models
from user_database_tg.db.models import Payment

BASE_DIR = Path(__file__).parent.parent.parent


async def init_tortoise(
        username=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        db_name=DB_DB_NAME,
):
    logger.debug(f"Инициализация BD {host}")
    await Tortoise.init(  # todo
        # _create_db=True,
        db_url=f"postgres://{username}:{password}@{host}:{port}/{db_name}",
        modules={"models": ["user_database_tg.db.models"]},
    )
    await Tortoise.generate_schemas()


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
    parser.add_argument(
        "-T",
        "--is_test",
        type=bool,
        default=False,
        help="Run in test mode",
        required=False,
    )
    parser.add_argument(
        "-T",
        "--is_test",
        type=bool,
        default=False,
        help="Run in test mode",
        required=False,
    )
    args = parser.parse_args()
    print(args)


def init_logging():
    logger.remove()
    logger.add(
        sink=sys.stderr,
        level="TRACE",
        enqueue=True,
        diagnose=True,
    )
    # logger.add(sink=Path(BASE_DIR, "logs/paylog.log"), level='TRACE', enqueue=True, encoding='utf-8', diagnose=True, )
    logger.add(
        sink=Path(BASE_DIR, "logs/database.log"),
        level="TRACE",
        enqueue=True,
        encoding="utf-8",
        diagnose=True,
        rotation="5MB",
        # compression="zip",
    )


async def dell_all():
    await init_db()
    for h in models.__all__:
        await getattr(models, h).all().delete()


async def main():
    await init_db()
    ps = await Payment.all().order_by("-date").limit(10)
    print(ps)


if __name__ == "__main__":
    init_logging()
    asyncio.run(main())
    # run_process_create_users(4)
    # asyncio.run(create_table())

    # asyncio.run(create_users())
    # mp_context =
    # asyncio.run(dell_all())
