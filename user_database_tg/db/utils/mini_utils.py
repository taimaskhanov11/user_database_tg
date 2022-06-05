import asyncio
import contextlib
import datetime
import json
from pathlib import Path

from dateutil import parser
from loguru import logger

from user_database_tg.config.config import BASE_DIR, TZ
from user_database_tg.db.db_main import init_tortoise
from user_database_tg.db.models import Subscription, DbUser, Payment, ApiSubscription
from user_database_tg.db.utils.backup import backup_name


def open_big_file(path, encoding="utf-8"):
    path = path or Path("/var/lib/postgresql/TO_IMPORT/unknown_site_name")
    with open(path, encoding=encoding) as f:
        for i in range(50):
            print(f.readline())


async def main():
    await init_tortoise(**{
        "username": "postgres",
        "password": "DpKeUf.0",
        "host": "188.130.139.157",
        "port": 5432,
        "db_name": "users_database",
    })

    with open(Path(BASE_DIR, "backup", f"{backup_name}.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    for data in data['data']:
        u, s, p = data
        s = await Subscription.create(**s)
        u = await DbUser.create(**u, subscription=s)
        p = await Payment.create(**p, db_user=u)
        logger.success(f"{data}")


async def main2():
    await init_tortoise(**{
        "username": "postgres",
        "password": "DpKeUf.0",
        "host": "188.130.139.157",
        "port": 5432,
        "db_name": "users_database",
    })

    with open(Path(BASE_DIR, f"users_database_public_dbuser.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    for user_data in data:
        del user_data["id"]
        del user_data["subscription_id"]
        del user_data["is_search"]
        user_data["register_data"] = parser.parse(user_data["register_data"])
        s = await Subscription.create(duration=datetime.datetime.now(TZ))
        u, _create = await DbUser.get_or_create(*user_data, subscription=s)
        # u, _create  = await DbUser.get_or_new(**user_data)
        logger.success(f"{u}, {_create}")


# @logger.catch
async def main3():
    await init_tortoise(**{
        "username": "postgres",
        "password": "DpKeUf.0",
        "host": "188.130.139.157",
        "port": 5432,
        "db_name": "users_database",
    })

    with open(Path(BASE_DIR, f"users_database_public_subscription.json"), "r", encoding="utf-8") as f, open(
            Path(BASE_DIR, f"users_database_public_dbuser.json"), "r", encoding="utf-8") as f2:
        sub_data:list[dict] = json.load(f)
        user_data:list[dict] = json.load(f2)
    # print(user_data)
    # return
    for user in user_data:
        try:
            for sub in sub_data:
                if user["subscription_id"] == sub["id"]:

                    user_copy = user.copy()
                    sub_copy = sub.copy()
                    del user_copy["id"]
                    del user_copy["subscription_id"]
                    del user_copy["is_search"]
                    user_copy["register_data"] = parser.parse(user_copy["register_data"])

                    del sub_copy["id"]

                    sub_copy["duration"] = parser.parse(sub_copy["duration"])
                    s = await Subscription.create(
                        **sub_copy
                    )
                    db_user = await DbUser.create(**user_copy, subscription=s)
                    await db_user.save()
                    logger.success(f"{user_copy},{sub_copy},{db_user}")

        except Exception as e:
            logger.warning(f"{user}.{e}")
async def main4():
    await init_tortoise(**{
        "username": "postgres",
        "password": "DpKeUf.0",
        "host": "188.130.139.157",
        "port": 5432,
        "db_name": "users_database",
    })

    for u in await DbUser.all().select_related("api_subscription"):
        try:
            if not u.api_subscription:
                await ApiSubscription.create(
                    duration=datetime.datetime.now(TZ),
                    db_user=u
                )
                logger.success(u)
        except Exception as e:
            logger.warning(f"{e},u{u.user_id}")


def t_util():
    date = "2022-03-20 15:55:43.904955 +00:00"
    date = parser.parse(date)
    print(date)
    print(type(date))


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(main4())
    # t_util()
    # find_email("aahaantourandtravels01@gmail.com:Yog@1987")
