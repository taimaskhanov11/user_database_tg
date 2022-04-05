import asyncio
import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from user_database_tg.config.config import BASE_DIR, TZ
from user_database_tg.db.db_main import init_logging, init_db, init_tortoise
from user_database_tg.db.models import (
    Subscription,
    Payment,
    DbUser,
)

backup_name = f"db_backup"


async def making_backup(interval):
    while True:
        await asyncio.sleep(interval)
        logger.debug("Резервное копирование запущено")
        # now_time = f"{datetime.now(TZ).timestamp()}"
        users: list[DbUser] = await DbUser.filter(subscription__is_subscribe=True).select_related("subscription")
        user_sub_pay: list[tuple[dict, dict, dict]] = []
        for u in users:
            # ps = []
            p = None
            p_d = None
            for p in await users[0].payments:
                pass
                # ps.append(p)
            u_d = dict(u)
            del u_d["id"]
            del u_d["subscription_id"]
            s_d = dict(u.subscription)
            del s_d["id"]

            if p:
                p_d = dict(p)
                del p_d["id"]
                del p_d["db_user_id"]

            user_sub_pay.append((u_d, s_d, p_d))

        data = {"data": user_sub_pay, "datetime": datetime.now(TZ)}
        with open(Path(BASE_DIR, "backup", f"{backup_name}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, sort_keys=True, default=str, indent=4, ensure_ascii=False)

        logger.info(f"Резервное копирование завершено {backup_name}")


async def restore_backup():
    init_logging()
    await init_db()
    # await making_backup(1)
    with open(
            Path(BASE_DIR, "backup", f"{backup_name}.json"),
            encoding="utf8",
    ) as f:
        data = json.load(f)
    logger.info(f"Восстановление backup... {data['datetime']}")
    user_sub_pay = data["data"]
    for u, s, p in user_sub_pay:
        s = await Subscription.create(**s)
        u = await DbUser.create(**u, subscription=s)
        if p:
            p = await Payment.create(**p, db_user=u)
    logger.success("Выгрузка успешно завершена")
    logger.success(f"Восстановление backup завершено {data['datetime']}")


async def main():
    init_logging()
    await init_tortoise()
    await making_backup(2)


if __name__ == "__main__":
    asyncio.run(restore_backup())
    # asyncio.run(main())
