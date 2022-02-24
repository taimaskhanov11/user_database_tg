import random

from aiogram import Dispatcher, types
from pyqiwip2p import QiwiP2P

from user_database_tg.app import markups
from user_database_tg.config.config import QIWI_TOKEN

p2p = QiwiP2P(auth_key=QIWI_TOKEN)


async def subscribe_day(call: types.CallbackQuery):  # todo 2/25/2022 1:14 AM taima: сделать универсальным
    comment = f"{call.from_user.id}_{random.randint(1000, 9999)}"
    bill = p2p.bill(amount=3, lifetime=15, comment=comment)
    # create bill #todo 2/25/2022 1:10 AM taima:
    await call.message.delete()
    await call.message.answer(
        "Подписка на день. 3 руб.\n"
        "После оплаты дождитесь сообщения от бота о поступлении оплаты."
        "Обычно это занимает до 5 минут.",
        reply_markup=markups.get_subscribe(bill.pay_url)
    )

async def subscribe_month(call: types.CallbackQuery):
    comment = f"{call.from_user.id}_{random.randint(1000, 9999)}"
    bill = p2p.bill(amount=30, lifetime=15, comment=comment)
    # create bill #todo 2/25/2022 1:10 AM taima:
    await call.message.delete()
    await call.message.answer(
        "Подписка на день. 10 руб.\n"
        "После оплаты дождитесь сообщения от бота о поступлении оплаты."
        "Обычно это занимает до 5 минут.",
        reply_markup=markups.get_subscribe(bill.pay_url)
    )


def register_handlers_subscriptions(dp: Dispatcher):
    dp.register_callback_query_handler(subscribe_day, text="subscribe_day")
    dp.register_callback_query_handler(subscribe_month, text="subscribe_month")
