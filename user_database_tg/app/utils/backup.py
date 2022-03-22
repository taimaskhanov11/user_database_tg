import asyncio
import collections
import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from user_database_tg.config.config import BASE_DIR, TZ
from user_database_tg.db.db_main import init_logging, init_db
from user_database_tg.db.models import (
    Subscription,
    Payment,
    DbUser,
    Billing,
    SubscriptionInfo,
    DbTranslation,
)

backup_name = f"db_backup"


async def making_backup(interval):
    while True:
        await asyncio.sleep(interval)
        logger.debug("Резервное копирование запущено")
        # now_time = f"{datetime.now(TZ).timestamp()}"
        data = collections.defaultdict(list)
        for s in await Subscription.filter(is_subscribe=True):
            data["subscriptions"].append(dict(s))

        for p in await Payment.all():
            data["payments"].append(dict(p))

        for u in await DbUser.all():
            data["users"].append(dict(u))

        for b in await Billing.all():
            data["billing"].append(dict(b))

        for si in await SubscriptionInfo.all():
            data["subscriptions_info"].append(dict(si))

        for tr in await DbTranslation.all():
            data["translations"].append(dict(tr))

        data["datetime"] = datetime.now(TZ)
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

    # for s in await Subscription.filter(is_subscribe=True):
    #     data["subscriptions"].append(dict(s))
    # for p in await Payment.all():
    #     data["payments"].append(dict(p))
    # for u in await DbUser.all():
    #     data["users"].append(dict(u))
    # for b in await Billing.all():
    #     data["billing"].append(dict(b))

    for si in data.get("subscriptions_info", ()):
        subi, is_created = await SubscriptionInfo.get_or_create(**si)
        if is_created:
            logger.debug(f"Шаблон для подписки {subi.title} создан")

    for s in data.get("subscriptions", ()):
        s, is_created = await Subscription.get_or_create(**s)
        if is_created:
            logger.debug(f"Подписка создана {s.title} создан")

    for u in data.get("users", ()):
        user, is_created = await DbUser.get_or_create(**u)
        if is_created:
            logger.debug(f"Пользователь {user.username} создан")
            for p in data.get("payments", ()):
                if p["db_user_id"] == user.pk:
                    # p_data = p["db_user_id"]
                    await Payment.create(**p)
                    logger.debug(f"Платеж для пользователя {user.username} создан")

            for b in data.get("billing", ()):
                if b["db_user_id"] == user.pk:
                    await Billing.create(**b)
                    logger.debug(f"Неоплаченный платеж для пользователя {user.username} создан")
            # for payments
    for tr in data.get("translations", ()):
        trans, is_created = await DbTranslation.get_or_create(**tr)
        if is_created:
            logger.debug(f"Перевод на {trans.title} создан")

    #
    # print(res)


if __name__ == "__main__":
    asyncio.run(restore_backup())
