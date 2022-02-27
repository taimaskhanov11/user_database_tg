import asyncio
import datetime

from loguru import logger

from user_database_tg.config.config import TZ
from user_database_tg.db.db_main import init_db
from user_database_tg.db.models import Subscription
from user_database_tg.loader import bot


@logger.catch
async def updating_the_daily_requests_limit(start=True):
    update_date = datetime.timedelta(hours=24, minutes=0, seconds=0)
    if start:
        dt = datetime.datetime.now(TZ)
        dttd = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
        update_date = update_date - dttd
    total_seconds = update_date.total_seconds()
    logger.debug(f"Ожидание ежедневного лимита запросов  |{start=}|{update_date}|{total_seconds}s")
    await asyncio.sleep(total_seconds) #todo 2/27/2022 2:06 PM taima:
    logger.debug(f"Обновление ежедневного лимита запросов  |{start=}|{update_date}|{total_seconds}s")
    # await asyncio.sleep(10)
    now_dt = datetime.datetime.now(TZ)
    for sub in await Subscription.all().select_related("db_user"):
        diff = sub.duration - now_dt
        logger.debug(f"Проверка подписки|\n{sub.db_user.username}|{sub.db_user.user_id}"
                     f"\n{sub.duration}>current {now_dt}\n"
                     f"{diff}| разница время подписки минус  сегодня\n"
                     f"{diff.total_seconds()} - сек")

        # Проверка подписки
        if sub.is_subscribe and now_dt > sub.duration:
            logger.debug(f"Подписка закончилась {repr(sub.db_user)} ")
            await bot.send_message(sub.db_user.user_id, f"Подписка {sub.title} закончилась")
            sub.db_user.subscription = await Subscription.create()
            await sub.db_user.save()
            # await sub.delete()
            continue

        sub.remaining_daily_limit = sub.daily_limit
        await sub.save()
        await bot.send_message(sub.db_user.user_id, f"Дневной лимит обновлен")
    # logger.info(
    #     f"Ежедневный лимит запросов обновлен |{start=}|{update_date}|{total_seconds}s. Следующая проверка через 24 часа")
    asyncio.create_task(updating_the_daily_requests_limit(start=False))


async def main():
    await init_db()
    await updating_the_daily_requests_limit()


if __name__ == '__main__':
    asyncio.run(main())
