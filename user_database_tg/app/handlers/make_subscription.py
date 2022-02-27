import random
import re

from aiogram import Dispatcher, types
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.filters.payment_filters import SubscribeFilter, RejectPaymentFilter
from user_database_tg.app.translation.message_data import Translation
from user_database_tg.app.utils.payment_processes import check_payment
from user_database_tg.config.config import p2p
from user_database_tg.db.models import DbUser, Billing


@logger.catch
async def subscribe(call: types.CallbackQuery, db_user: DbUser, translation: Translation):
    logger.critical(db_user)
    bill = await Billing.get_or_none(db_user=db_user)
    if bill:
        await call.message.delete()
        await call.message.answer(
            translation.wait_payment, reply_markup=markups.get_subscribe_menu(translation, wait=True)
        )
    else:
        duration, day_limit, amount = re.findall(r"_d(.*)_(.*)_(.*)", call.data)[0]
        days = int(duration) * 30
        comment = f"{call.from_user.id}_{duration}_{random.randint(1000, 9999)}"
        bill_id = f"{str(call.from_user.id)[-6:-1]}{random.randint(1, 9999)}"
        bill = await p2p.bill(bill_id=int(bill_id), amount=amount, lifetime=15, comment=comment)
        await Billing.create_bill(db_user, bill.bill_id, amount, duration, day_limit)  # todo 2/26/2022 7:07 PM taima:
        await call.message.delete()
        call = await call.message.answer(
            translation.create_payment.format(days=days, amount=amount),
            reply_markup=markups.get_subscribe(bill.pay_url, translation)
        )
        await check_payment(bill.bill_id, db_user.user_id, call)


@logger.catch
async def reject_payment(call: types.CallbackQuery, db_user: DbUser, translation: Translation):
    bill_obj = await Billing.get(db_user=db_user).select_related("subscription")
    bill = await p2p.reject(bill_obj.bill_id)
    await bill_obj.delete()
    # await bill_obj.subscription.delete()

    await call.message.delete()
    logger.info(f"{call.from_user.id}|Оплата {bill_obj.bill_id}|{bill.status} отменена ")
    await call.message.answer(translation.reject_payment.format(title=bill_obj.subscription.title))


def register_subscriptions_handlers(dp: Dispatcher):
    # dp.register_callback_query_handler(subscribe, text_startswith="subscribe_")
    # dp.register_callback_query_handler(reject_payment, text="reject_payment")
    dp.register_callback_query_handler(subscribe, SubscribeFilter())
    dp.register_callback_query_handler(reject_payment, RejectPaymentFilter())
    # dp.register_callback_query_handler(subscribe_month, text="subscribe_month")
