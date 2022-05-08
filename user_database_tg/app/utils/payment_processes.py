import asyncio
from datetime import datetime, timedelta

import aiohttp
from aiogram import types
from loguru import logger

from user_database_tg.config import config
from user_database_tg.config.config import p2p, TZ
from user_database_tg.db.models import Billing, DbUser, Limit, Payment, APIBilling
from user_database_tg.loader import bot


async def create_bill(call: types.CallbackQuery):
    pass


@logger.catch
async def check_payment(bill_id, db_user):  # todo 2/28/2022 8:53 PM taima: поправить
    bill = await p2p.check(bill_id=bill_id)

    if bill.status == "PAID":
        logger.info(f"{db_user.user_id}|{bill.bill_id} успешно оплачен")
        db_bill = await Billing.get(bill_id=bill_id).prefetch_related("subscription")

        Limit.lats_day_amount_payments += db_bill.amount
        await Payment.create(db_user=db_user, date=datetime.now(TZ), amount=db_bill.amount)
        if db_user.subscription.title == db_bill.subscription.title:
            db_user.subscription.days_duration += db_bill.subscription.days_duration
            db_user.subscription.duration += timedelta(db_bill.subscription.days_duration)

            await db_user.subscription.save()
            await db_user.save()
            await db_bill.subscription.delete()
            await db_bill.delete()

            logger.info("Обновлена существующая подписка")
            await bot.send_message(db_user.user_id, "Обновлена существующая подписка")

        else:
            db_bill.subscription.is_paid = (
                True  ##todo 2/28/2022 9:20 PM taima: Добавить оставшиеся дни в новую подписку
            )
            old_sub = db_user.subscription
            db_user.subscription = db_bill.subscription

            await db_user.subscription.save()
            await db_user.save()
            await db_bill.delete()
            await old_sub.delete()
            logger.info("Создана новая подписка")

        logger.info("Информация о подписке успешно обновлена")
        return True
    return False


async def add_api_token(user_token):
    async with aiohttp.ClientSession() as session:
        data = {
            "token": config.MAIN_API_TOKEN,
            "user_token": user_token
        }
        async with session.post(f"http://localhost:8000/api/v1/token/", json=data) as res:
            logger.info(await res.text())


@logger.catch
async def check_payment_api(bill_id, db_user: DbUser):  # todo 2/28/2022 8:53 PM taima: поправить
    bill = await p2p.check(bill_id=bill_id)

    if bill.status == "PAID":
        logger.info(f"{db_user.user_id}|{bill.bill_id} успешно оплачен")
        db_bill: APIBilling = await APIBilling.get(bill_id=bill_id).prefetch_related("api_subscription")
        Limit.lats_day_amount_payments += db_bill.amount
        await Payment.create(db_user=db_user, date=datetime.now(TZ), amount=db_bill.amount)

        if db_user.api_subscription.title == db_bill.api_subscription.title:
            db_user.api_subscription.days_duration += db_bill.api_subscription.days_duration
            db_user.api_subscription.duration += timedelta(db_bill.api_subscription.days_duration)

            await db_user.api_subscription.save()
            await db_user.save()
            await db_bill.api_subscription.delete()
            await db_bill.delete()

            logger.info("Обновлена существующая подписка")
            await bot.send_message(db_user.user_id, "Обновлена существующая подписка")

        else:
            db_bill.api_subscription.is_paid = (
                True  ##todo 2/28/2022 9:20 PM taima: Добавить оставшиеся дни в новую подписку
            )
            old_sub = db_user.api_subscription
            await old_sub.delete()
            # await db_user.refresh_from_db()
            db_bill.api_subscription.db_user = db_user
            # db_user.api_subscription = db_bill.api_subscription
            # await db_user.api_subscription.save()
            await db_bill.api_subscription.save()
            await db_user.save()
            await db_bill.delete()
            asyncio.create_task(add_api_token(db_bill.api_subscription.token))

            logger.info("Создана новая подписка")

        logger.info("Информация о подписке успешно обновлена")
        return True
    return False


@logger.catch
async def check_payment2(bill_id, user_id, message: types.Message):  # todo 2/27/2022 3:08 PM taima:  translation
    for _ in range(30):
        bill = await p2p.check(bill_id=bill_id)
        if bill.status == "PAID":
            # if True:
            logger.info(f"{user_id}|{bill.bill_id} успешно оплачен")
            db_bill = await Billing.get(bill_id=bill_id).prefetch_related("subscription")
            db_user = await DbUser.filter(user_id=user_id).select_related("subscription").first()
            db_bill.subscription.is_paid = True
            old_sub = db_user.subscription
            db_user.subscription = db_bill.subscription

            await db_user.subscription.save()
            await db_user.save()
            await db_bill.delete()
            await old_sub.delete()
            await message.delete()
            await bot.send_message(user_id, f"Подписка [{db_bill.subscription.title}] успешно оплачена!")
            break

        elif bill.status == "REJECTED":
            logger.debug(f"Чек {user_id}|{bill_id} отменен, остановка проверки")
            # db_bill = await Billing.get_or_none(bill_id=bill_id) #todo 2/26/2022 11:29 AM taima:
            # if db_bill:
            #     await bot.send_message(user_id, "Подписка успешно удалена!")
            #     await db_bill.delete()
            # await bot.send_message(user_id, "Подписка успешно отменена!")

            break
        await asyncio.sleep(30)
