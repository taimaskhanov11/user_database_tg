import random
import re
from unittest.mock import Mock

import aiohttp
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.filters.payment_filters import (
    RejectPaymentFilterAPI,
    SubscribeFilterAPI,
    AcceptPaymentFilterAPI,
    ViewSubscriptionFilterAPI, MainPaymentFilter,
)
from user_database_tg.app.subscription.subscription_info import SUBSCRIPTIONS_INFO_API
from user_database_tg.app.utils.payment_processes import check_payment_api
from user_database_tg.config.config import p2p, CRYPTO_SHOP_ID, CRYPTO_API_KEY
from user_database_tg.db.models import DbUser, DbTranslation, APIBilling


class BuySubscriptionAPI(StatesGroup):
    start = State()


async def view_subscription(call: types.CallbackQuery, translation: DbTranslation):
    try:
        sub_info = SUBSCRIPTIONS_INFO_API.get(int(re.findall(r"view_buy_api_(\d*)", call.data)[0]))
        await call.message.delete()
        await call.message.answer(
            f"{sub_info}",
            reply_markup=markups.get_subscribe_menu_pay_api(sub_info.pk, translation),
        )
    except ValueError as e:
        logger.critical(e)
        await call.message.answer("Нет подписок")


async def create_subscribe_start(call: types.CallbackQuery, db_user: DbUser, translation: DbTranslation,
                                 state: FSMContext):
    sub_info = SUBSCRIPTIONS_INFO_API.get(int(re.findall(r"_api_(\d*)", call.data)[0]))
    await state.update_data(sub_api_info=sub_info)
    await call.message.answer(f"Выберите способ оплаты", reply_markup=markups.create_subscribe_start())
    await BuySubscriptionAPI.start.set()


async def create_subscribe(call: types.CallbackQuery, db_user: DbUser, translation: DbTranslation, state: FSMContext):
    logger.critical(db_user.user_id)
    bill_db = await APIBilling.get_or_none(db_user=db_user).select_related("api_subscription")
    payment_type = call.data

    if bill_db:
        try:
            if bill_db.payment_type == "qiwi":
                bill = await p2p.check(bill_db.bill_id)
            else:
                bill = Mock()
                bill.pay_url = bill_db.pay_url

            await call.message.delete()
            await call.message.answer(
                f"{translation.wait_payment}\n{bill_db.api_subscription.title}",
                # reply_markup=markups.get_subscribe_menu(translation, wait=True),
                reply_markup=markups.get_subscribe_payment_api(bill.pay_url, translation),
            )
            await state.finish()

            return
        except Exception as e:
            await bill_db.delete()
            logger.critical(e)

    data = await state.get_data()
    # sub_info = SUBSCRIPTIONS_INFO_API.get(int(re.findall(r"_api_(\d*)", call.data)[0]))
    sub_info = data["sub_api_info"]
    if payment_type == "qiwi":
        comment = f"{call.from_user.id}_{sub_info.days}_{random.randint(1000, 9999)}"
        bill_id = f"{str(call.from_user.id)[-6:-1]}{random.randint(1, 9999)}"
        bill = await p2p.bill(bill_id=int(bill_id), amount=sub_info.price, lifetime=15, comment=comment)
        db_bill = await APIBilling.create_bill(db_user, bill.bill_id, sub_info)  # todo 2/26/2022 7:07 PM taima:

    else:
        data = dict(
            amount=sub_info.price,
            currency="RUB",
            shop_id=CRYPTO_SHOP_ID
        )
        async with aiohttp.ClientSession(headers={"Authorization": f"Token {CRYPTO_API_KEY}"}) as session:
            async with session.post("https://cryptocloud.pro/api/v2/invoice/create", data=data) as res:
                res_data = await res.json()
                db_bill = await APIBilling.create_bill(db_user,
                                                       res_data["invoice_id"],
                                                       sub_info,
                                                       "crypto",
                                                       res_data["pay_url"])  # todo 2/26/2022 7:07 PM taima:
            bill = Mock()
            bill.pay_url = res_data["pay_url"]

    await call.message.delete()
    await call.message.answer(
        f"{translation.create_payment.format(title=db_bill.api_subscription.title)}\n"
        f"Для криптовалюты оплата происходит в течении 10 минут автоматически",
        reply_markup=markups.get_subscribe_payment_api(bill.pay_url, translation),
    )
    await state.finish()

    # await check_payment(bill.bill_id, db_user.user_id)


async def reject_payment(call: types.CallbackQuery, db_user: DbUser, translation: DbTranslation):
    try:
        await call.answer()
        bill_obj = await APIBilling.get(db_user=db_user).select_related("api_subscription")
        if bill_obj.payment_type == "qiwi":
            bill = await p2p.reject(bill_obj.bill_id)
        await bill_obj.delete()
        await bill_obj.api_subscription.delete()
        await call.message.delete()
        logger.info(f"{call.from_user.id}|Оплата {bill_obj.bill_id}| отменена ")
        await call.message.answer(translation.reject_payment.format(title=bill_obj.api_subscription.title))
    except Exception as e:
        logger.exception(e)


async def accept_payment(call: types.CallbackQuery, db_user: DbUser, translation: DbTranslation):
    db_bill = await APIBilling.get(db_user=db_user).select_related("api_subscription")
    is_paid = await check_payment_api(db_bill, db_user)

    if is_paid:
        await call.message.delete()
        await call.message.answer(
            # f"Подписка {db_bill.subscription.title} успешно оплачена!"
            translation.accept_payment.format(title=db_bill.api_subscription.title)
        )
    else:
        # await call.answer("❗️ Платеж не найден")
        await call.answer(f"{translation.payment_not_found}.\nДля крипты проверка в течении 10 минут.")


def register_subscriptions_api_handlers(dp: Dispatcher):
    # dp.register_callback_query_handler(subscribe, text_startswith="subscribe_")
    dp.register_callback_query_handler(view_subscription, ViewSubscriptionFilterAPI())

    dp.register_callback_query_handler(create_subscribe_start, SubscribeFilterAPI())
    dp.register_callback_query_handler(create_subscribe, MainPaymentFilter(), state=BuySubscriptionAPI.start)

    dp.register_callback_query_handler(reject_payment, RejectPaymentFilterAPI())
    dp.register_callback_query_handler(accept_payment, AcceptPaymentFilterAPI())

    # dp.register_callback_query_handler(subscribe_month, text="subscribe_month")
