import random
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.filters.payment_filters import (
    RejectPaymentFilter,
    SubscribeFilter,
    AcceptPaymentFilter,
    ViewSubscriptionFilter,
)
from user_database_tg.app.subscription.subscription_info import SUBSCRIPTIONS_INFO
from user_database_tg.app.translation.message_translation import Translation
from user_database_tg.app.utils.payment_processes import check_payment
from user_database_tg.config.config import p2p
from user_database_tg.db.models import Billing, DbUser, DbTranslation, Limit


class BuySubscription(StatesGroup):
    start = State()


async def view_subscription(call: types.CallbackQuery, translation: DbTranslation):
    try:
        sub_info = SUBSCRIPTIONS_INFO.get(
            int(re.findall(r"view_buy_(\d*)", call.data)[0])
        )
        await call.message.delete()
        await call.message.answer(
            f"{sub_info}",
            reply_markup=markups.get_subscribe_menu_pay(sub_info.pk, translation),
        )
    except ValueError as e:
        logger.critical(e)
        await call.message.answer("Нет подписок")


@logger.catch
async def create_subscribe(
    call: types.CallbackQuery, db_user: DbUser, translation: DbTranslation
):
    logger.critical(db_user)
    bill_db = await Billing.get_or_none(db_user=db_user).select_related("subscription")
    if bill_db:
        bill = await p2p.check(bill_db.bill_id)
        await call.message.delete()
        await call.message.answer(
            f"{translation.wait_payment}\n{bill_db.subscription.title}",
            # reply_markup=markups.get_subscribe_menu(translation, wait=True),
            reply_markup=markups.get_subscribe_payment(bill.pay_url, translation),
        )
    else:
        sub_info = SUBSCRIPTIONS_INFO.get(int(re.findall(r"_(\d*)", call.data)[0]))

        comment = f"{call.from_user.id}_{sub_info.days}_{random.randint(1000, 9999)}"
        bill_id = f"{str(call.from_user.id)[-6:-1]}{random.randint(1, 9999)}"
        bill = await p2p.bill(
            bill_id=int(bill_id), amount=sub_info.price, lifetime=15, comment=comment
        )
        db_bill = await Billing.create_bill(
            db_user, bill.bill_id, sub_info
        )  # todo 2/26/2022 7:07 PM taima:

        await call.message.delete()
        await call.message.answer(
            translation.create_payment.format(title=db_bill.subscription.title),
            reply_markup=markups.get_subscribe_payment(bill.pay_url, translation),
        )
        # await check_payment(bill.bill_id, db_user.user_id)


@logger.catch
async def reject_payment(
    call: types.CallbackQuery, db_user: DbUser, translation: DbTranslation
):
    bill_obj = await Billing.get(db_user=db_user).select_related("subscription")
    bill = await p2p.reject(bill_obj.bill_id)
    await bill_obj.delete()
    await bill_obj.subscription.delete()
    await call.message.delete()
    logger.info(
        f"{call.from_user.id}|Оплата {bill_obj.bill_id}|{bill.status} отменена "
    )
    await call.message.answer(
        translation.reject_payment.format(title=bill_obj.subscription.title)
    )


async def accept_payment(
    call: types.CallbackQuery, db_user: DbUser, translation: DbTranslation
):
    db_bill = await Billing.get(db_user=db_user).select_related("subscription")
    is_paid = await check_payment(db_bill.bill_id, db_user)

    if is_paid:
        await call.message.delete()
        await call.message.answer(
            # f"Подписка {db_bill.subscription.title} успешно оплачена!"
            translation.accept_payment.format(title=db_bill.subscription.title)
        )
    else:
        # await call.answer("❗️ Платеж не найден")
        await call.answer(translation.payment_not_found)


def register_subscriptions_handlers(dp: Dispatcher):
    # dp.register_callback_query_handler(subscribe, text_startswith="subscribe_")
    dp.register_callback_query_handler(view_subscription, ViewSubscriptionFilter())
    dp.register_callback_query_handler(create_subscribe, SubscribeFilter())
    dp.register_callback_query_handler(reject_payment, RejectPaymentFilter())
    dp.register_callback_query_handler(accept_payment, AcceptPaymentFilter())

    # dp.register_callback_query_handler(subscribe_month, text="subscribe_month")
