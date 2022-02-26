import asyncio

from aiogram import types
from loguru import logger

from user_database_tg.config.config import p2p
from user_database_tg.db.models import Billing
from user_database_tg.loader import bot


async def create_bill(call: types.CallbackQuery):
    pass


async def check_payment(bill_id, user_id):
    for _ in range(15):
        bill = await p2p.check(bill_id=bill_id)
        if bill.status == "PAID":
            db_bill = await Billing.get(bill_id=bill_id).select_related("subscription")
            db_bill.user = db_bill.subscription
            await db_bill.user.save()
            await db_bill.delete()
            await bot.send_message(user_id, "Подписка успешно оплачена!")

        elif bill.status == "REJECTED":
            logger.debug(f"Чек {user_id}|{bill_id} отменен, остановка проверки")
            # db_bill = await Billing.get_or_none(bill_id=bill_id) #todo 2/26/2022 11:29 AM taima:
            # if db_bill:
            #     await bot.send_message(user_id, "Подписка успешно удалена!")
            #     await db_bill.delete()
            # await bot.send_message(user_id, "Подписка успешно отменена!")

            break
        await asyncio.sleep(3)
