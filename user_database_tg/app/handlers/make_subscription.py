import random
import re

from aiogram import Dispatcher, types
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.messages.menu import SUBSCRIBE_PRE
from user_database_tg.app.utils.payment_processes import check_payment
from user_database_tg.config.config import p2p
from user_database_tg.db.models import DbUser, Billing


@logger.catch
async def subscribe(call: types.CallbackQuery):  # todo 2/25/2022 1:14 AM taima: сделать универсальным
    user = await DbUser.get_or_new(call.from_user.id, call.from_user.username)
    bill = await Billing.get_or_none(user=user)
    if bill:
        await call.message.answer(f"Ожидание оплаты предыдущего запроса",
                                  reply_markup=markups.get_subscribe_menu(wait=True))
        return

    duration, day_limit, amount = re.findall(r"_d(.*)_(.*)_(.*)", call.data)[0]
    days = int(duration) * 30
    comment = f"{call.from_user.id}_{duration}_{random.randint(1000, 9999)}"
    bill_id = f"{str(call.from_user.id)[-6:-1]}{random.randint(1, 9999)}"
    bill = await p2p.bill(bill_id=int(bill_id), amount=amount, lifetime=15, comment=comment)
    logger.critical(bill.bill_id)
    await Billing.create_receipt(user, bill.bill_id, amount, duration, day_limit)
    await call.message.delete()
    await call.message.answer(
        SUBSCRIBE_PRE.format(days=days, amount=amount),
        reply_markup=markups.get_subscribe(bill.pay_url)
    )
    await check_payment(bill.bill_id, call.from_user.id)


@logger.catch
async def reject_payment(call: types.CallbackQuery):
    user = await DbUser.get_or_new(call.from_user.id, call.from_user.username)
    bill = await Billing.get(user=user).select_related("subscription")
    bill = await p2p.reject(bill.bill_id)
    logger.info(f"{call.from_user.id}|Оплата {bill.bill_id}|{bill.status} отменена ")
    await call.message.answer(f"Оплата на подписку {bill.subscription.title} отменена")


def register_handlers_subscriptions(dp: Dispatcher):
    dp.register_callback_query_handler(subscribe, text_startswith="subscribe_")
    dp.register_callback_query_handler(reject_payment, text="reject_payment")
    # dp.register_callback_query_handler(subscribe_month, text="subscribe_month")
