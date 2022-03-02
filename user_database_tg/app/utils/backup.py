import asyncio
import collections
import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from user_database_tg.config.config import BASE_DIR, TZ
from user_database_tg.db.models import Subscription, Payment, DbUser


async def making_backup(interval):
    while True:
        await asyncio.sleep(interval)
        logger.debug("Резервное копирование запущено")
        # now_time = f"{datetime.now(TZ).timestamp()}"
        now_time = f"main_data"  # todo 3/2/2022 12:17 AM taima:

        data = collections.defaultdict(list)
        for s in await Subscription.filter(is_subscribe=True):
            data["subscriptions"].append(dict(s))
        for p in await Payment.all():
            data["payments"].append(dict(p))
        for u in await DbUser.all():
            data["users"].append(dict(u))

        data["datetime"] = datetime.now(TZ)
        with open(Path(BASE_DIR, "backup", f"{now_time}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, sort_keys=True, default=str)

        logger.info(f"Резервное копирование завершено {now_time}")
