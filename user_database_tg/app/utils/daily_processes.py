import asyncio
import datetime

import aiohttp
from loguru import logger

from user_database_tg.config import config
from user_database_tg.config.config import TZ
from user_database_tg.db.db_main import init_db
from user_database_tg.db.models import Subscription, Limit, ApiSubscription
from user_database_tg.loader import bot


async def delete_api_token(user_token):
    async with aiohttp.ClientSession() as session:
        data = {
            "token": config.MAIN_API_TOKEN,
            "user_token": user_token
        }
        async with session.delete(f"http://localhost:8000/api/v1/token/", json=data) as res:
            logger.info(await res.text())


async def refresh_subscription():
    now_dt = datetime.datetime.now(TZ)
    for sub in await Subscription.all().select_related("db_user"):
        logger.debug(f"Проверка подписки {sub}")
        if sub.db_user:
            try:
                diff = sub.duration - now_dt
                logger.debug(
                    f"Проверка подписки|\n{sub.db_user.username}|{sub.db_user.user_id}"
                    f"\n{sub.duration}>current {now_dt}\n"
                    f"{diff}| разница время подписки минус  сегодня\n"
                    f"{diff.total_seconds()} - сек"
                )
                if sub.days_duration > 0:
                    sub.days_duration -= 1

                # Проверка подписки
                # if sub.is_subscribe and (now_dt > sub.duration or sub.days_duration <= 0):
                if sub.is_subscribe and sub.days_duration <= 0:
                    logger.debug(f"Подписка закончилась {sub.db_user.username} ")

                    await bot.send_message(sub.db_user.user_id, f"Подписка {sub.title} закончилась")
                    sub.db_user.subscription = await Subscription.create(duration=datetime.datetime.now(TZ))
                    await sub.db_user.save()
                    await sub.delete()
                    continue

                if sub.is_subscribe:
                    sub.remaining_daily_limit = sub.daily_limit
                else:
                    sub.remaining_daily_limit = config.DAILY_LIMIT

                await sub.save()
                logger.success(
                    f"{sub.db_user.username}[{sub.db_user.user_id}]|Дневной лимит запросов обновлен.({sub.remaining_daily_limit})")
            except Exception as e:
                logger.critical(f"Ошибка при обновлении лимитов {e}")


async def refresh_subscription_api():
    now_dt = datetime.datetime.now(TZ)
    for sub in await ApiSubscription.all().select_related("db_user"):
        logger.debug(f"Проверка подписки {sub}")
        if sub.db_user:
            try:
                diff = sub.duration - now_dt
                logger.debug(
                    f"Проверка подписки|\n{sub.db_user.username}|{sub.db_user.user_id}"
                    f"\n{sub.duration}>current {now_dt}\n"
                    f"{diff}| разница время подписки минус  сегодня\n"
                    f"{diff.total_seconds()} - сек"
                )

                if sub.days_duration > 0:
                    sub.days_duration -= 1

                # Проверка подписки
                if sub.is_subscribe and (now_dt > sub.duration or sub.days_duration <= 0):
                    logger.debug(f"Подписка закончилась {repr(sub.db_user)} ")
                    await bot.send_message(sub.db_user.user_id, f"Подписка {sub.title} закончилась")
                    await sub.delete()
                    await ApiSubscription.create(
                        duration=datetime.datetime.now(TZ),
                        db_user=sub.db_user
                    )
                    await sub.db_user.save()
                    asyncio.create_task(delete_api_token(sub.token))
                    continue

                await sub.save()
                logger.success(
                    f"{sub.db_user.username}[{sub.db_user.user_id}]|Дневной лимит запросов обновлен.({sub.remaining_daily_limit})")
            except Exception as e:
                logger.critical(f"Ошибка при обновлении лимитов {e}")


@logger.catch
async def everyday_processes(start=True):
    update_date = datetime.timedelta(hours=24, minutes=0, seconds=0)
    # update_date = datetime.timedelta(seconds=10)
    if start:
        dt = datetime.datetime.now(TZ)
        dttd = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
        update_date = update_date - dttd
    total_seconds = update_date.total_seconds()
    logger.debug(f"Ожидание ежедневного лимита запросов  |{start=}|{update_date}|{total_seconds}s")
    await asyncio.sleep(total_seconds)  # todo 2/27/2022 2:06 PM taima:
    asyncio.create_task(everyday_processes(start=False))
    logger.debug(f"Обновление ежедневного лимита запросов  |{start=}|{update_date}|{total_seconds}s")
    # await asyncio.sleep(10)
    await refresh_subscription()
    await refresh_subscription_api()
    Limit.daily_process()
    logger.debug("Дневные процессы обновлены")
    logger.info(
        f"Ежедневный лимит запросов обновлен |{start=}|{update_date}|{total_seconds}s. Следующая проверка через 24 часа"
    )


async def main():
    await init_db()
    # await everyday_processes()
    await refresh_subscription()


if __name__ == "__main__":
    asyncio.run(main())
