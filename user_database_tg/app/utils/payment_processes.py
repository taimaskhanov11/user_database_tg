import asyncio

from aiogram import types
from loguru import logger

from user_database_tg.config.config import p2p
from user_database_tg.db.models import Billing, DbUser
from user_database_tg.loader import bot


async def create_bill(call: types.CallbackQuery):
    pass


@logger.catch
async def check_payment(bill_id, user_id, message: types.Message):  # todo 2/27/2022 3:08 PM taima:  translation
    for _ in range(30):
        bill = await p2p.check(bill_id=bill_id)
        if bill.status == "PAID":
            # if True:
            logger.info(f"{user_id}|{bill.bill_id} успешно оплачен")
            db_bill = await Billing.get(bill_id=bill_id).prefetch_related("subscription")
            db_user = await DbUser.get(user_id=user_id).select_related("subscription")
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
