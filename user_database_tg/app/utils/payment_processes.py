import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock

import aiohttp
from aiogram import types
from loguru import logger

from user_database_tg.api.outgoing_requests import update_hash_requests
from user_database_tg.config import config
from user_database_tg.config.config import p2p, TZ, CRYPTO_API_KEY
from user_database_tg.db.models import Billing, DbUser, Limit, Payment, APIBilling
from user_database_tg.loader import bot


async def create_bill(call: types.CallbackQuery):
    pass


async def check_crypto_payment(db_bill: Billing | APIBilling):
    async with aiohttp.ClientSession(headers={"Authorization": f"Token {CRYPTO_API_KEY}"}) as session:
        async with session.get("https://cryptocloud.plus/api/v2/invoice/status",
                               params={"uuid": db_bill.bill_id}) as res:
            result = await res.json()
            logger.info(result)
            if result["status_invoice"] == "paid":
                return True
    return False


async def checking_api_purchases():
    logger.trace("Checking purchases")
    logger.trace(f"Check cls APIBilling")
    billings = await APIBilling.filter(expire_at__gte=datetime.now(TZ), payment_type="crypto")
    for invoice in billings:
        logger.trace(f"Check invoice {invoice.bill_id}[{invoice.amount}]")
        if await check_crypto_payment(invoice):
            await invoice.fetch_related("db_user__api_subscription", "api_subscription")
            await accept_api_payment(invoice, invoice.db_user)
            # await invoice.delete()
            logger.success(
                f"The invoice [{Billing.__name__}] [{invoice.db_user}]{invoice.amount} r"
                f"has been successfully paid")
            # await invoice.subscription_template
            await bot.send_message(invoice.db_user.user_id,
                                   "✅ Подписка {} успешно оплачена".format(invoice.api_subscription.title))


async def checking_purchases():
    logger.trace("Checking purchases")
    logger.trace(f"Check cls Billing")
    billings = await Billing.filter(expire_at__gte=datetime.now(TZ), payment_type="crypto")
    for invoice in billings:
        logger.trace(f"Check invoice {invoice.bill_id}[{invoice.amount}]")
        if await check_crypto_payment(invoice):
            await invoice.fetch_related("db_user__subscription", "subscription")
            await accept_payment(invoice, invoice.db_user)
            # await invoice.delete()
            logger.success(
                f"The invoice [{Billing.__name__}] [{invoice.db_user}]{invoice.amount} rub "
                f"has been successfully paid")
            # await invoice.subscription_template
            await bot.send_message(invoice.db_user.user_id,
                                   "✅ Подписка {} успешно оплачена".format(invoice.subscription.title))


MONTHS = {
    30: 1
}


async def accept_payment(db_bill, db_user: DbUser):
    logger.info(f"{db_user.user_id}|{db_bill.bill_id} успешно оплачен")
    db_bill = await Billing.get(bill_id=db_bill.bill_id).prefetch_related("subscription")

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

        if db_user.subscription.daily_limit is None:
            logger.info("Обновление лимитов в @Hash2PassBot")
            sub = db_user.subscription

            res = await update_hash_requests(db_user, sub.days_duration // 30)
            logger.success(f"Лимиты пользователя {db_user.user_id} обновлены на {res}")
            await bot.send_message(db_user.user_id, "Получены бесплатные запросы в партнерском боте @Hash2PassBot")

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

        if db_user.subscription.daily_limit is None:
            logger.info("Обновление лимитов в @Hash2PassBot")
            sub = db_user.subscription

            res = await update_hash_requests(db_user, sub.days_duration // 30)
            logger.success(f"Лимиты пользователя {db_user.user_id} обновлены на {res}")
            await bot.send_message(db_user.user_id, "Получены бесплатные запросы в партнерском боте @Hash2PassBot")

        logger.info("Создана новая подписка")

    logger.info("Информация о подписке успешно обновлена")


@logger.catch
async def check_payment_api(db_bill: APIBilling, db_user: DbUser):  # todo 2/28/2022 8:53 PM taima: поправить

    if db_bill.payment_type == "qiwi":
        bill = await p2p.check(bill_id=db_bill.bill_id)
        logger.info(bill)
    else:
        bill = Mock()
        bill.bill_id = db_bill.bill_id
        if await check_crypto_payment(db_bill):
            bill.status = "PAID"
        else:
            bill.status = "PENDING"

    if bill.status == "PAID":
        await accept_api_payment(db_bill, db_user)
        return True
    return False


@logger.catch
async def check_payment(db_bill: Billing, db_user: DbUser):  # todo 2/28/2022 8:53 PM taima: поправить

    if db_bill.payment_type == "qiwi":
        bill = await p2p.check(bill_id=db_bill.bill_id)
        logger.info(bill)
    else:
        bill = Mock()
        bill.bill_id = db_bill.bill_id
        if await check_crypto_payment(db_bill):
            bill.status = "PAID"
        else:
            bill.status = "PENDING"

    if bill.status == "PAID":
        await accept_payment(db_bill, db_user)
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


async def accept_api_payment(db_bill: APIBilling, db_user):
    logger.info(f"{db_user.user_id}|{db_bill.bill_id} успешно оплачен")
    db_bill: APIBilling = await APIBilling.get(bill_id=db_bill.bill_id).prefetch_related("api_subscription")
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
