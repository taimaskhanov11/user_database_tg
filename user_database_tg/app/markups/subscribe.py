from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from user_database_tg.app.subscription.subscription_info import SUBSCRIPTIONS_INFO
from user_database_tg.db.models import DbTranslation


def get_subscribe_menu_pay(pk: int, translation: DbTranslation):
    btn_pay = [
        InlineKeyboardButton(text=translation.go_payment_b, callback_data=f"subscribe_{pk}")
    ]

    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=[btn_pay],
        # row_width=3
    )
    return subscribe_menu


def get_subscribe_menu_view():
    btns_subscribe = [
        [InlineKeyboardButton(text=sub.title, callback_data=f"view_buy_{pk}")]
        for pk, sub in SUBSCRIPTIONS_INFO.items()
    ]

    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=btns_subscribe,
        # row_width=3
    )

    return subscribe_menu


def get_subscribe_payment(url, translation: DbTranslation):
    qiwi_menu = InlineKeyboardMarkup()
    btn_url = InlineKeyboardButton(text=translation.go_payment_b, url=url)
    btn_accept = InlineKeyboardButton(
        # text="⌛️Я ОПЛАТИЛ", callback_data="accept_payment"  # todo 2/28/2022 6:15 PM taima:
        text=translation.accept_payment_b,
        callback_data="accept_payment",  # todo 2/28/2022 6:15 PM taima:
    )
    btn_reject = InlineKeyboardButton(
        text=translation.reject_payment_b, callback_data="reject_payment"
    )
    qiwi_menu.add(btn_url)
    qiwi_menu.add(btn_accept)
    qiwi_menu.add(btn_reject)
    return qiwi_menu
