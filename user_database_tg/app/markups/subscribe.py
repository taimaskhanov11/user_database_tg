from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from user_database_tg.app.subscription.subscription_info import SUBSCRIPTIONS_INFO, SUBSCRIPTIONS_INFO_API
from user_database_tg.db.models import DbTranslation


def get_subscribe_menu_pay(pk: int, translation: DbTranslation):
    btn_pay = [InlineKeyboardButton(text=translation.go_payment_b, callback_data=f"subscribe_{pk}")]

    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=[btn_pay],
        # row_width=3
    )
    return subscribe_menu


def get_subscribe_menu_pay_api(pk: int, translation: DbTranslation):
    btn_pay = [InlineKeyboardButton(text=translation.go_payment_b, callback_data=f"subscribe_api_{pk}")]

    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=[btn_pay],
        # row_width=3
    )
    return subscribe_menu


def get_subscribe_menu_view():
    btns_subscribe = [
        [InlineKeyboardButton(text=sub.title, callback_data=f"view_buy_{pk}")] for pk, sub in SUBSCRIPTIONS_INFO.items()
    ]

    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=btns_subscribe,
        # row_width=3
    )

    return subscribe_menu


def get_subscribe_menu_view_api():
    btns_subscribe = [
        [InlineKeyboardButton(text=sub.title, callback_data=f"view_buy_api_{pk}")] for pk, sub in
        SUBSCRIPTIONS_INFO_API.items()
    ]

    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=btns_subscribe,
        # row_width=3
    )
    return subscribe_menu


def create_subscribe_start():
    qiwi_menu = InlineKeyboardMarkup()
    qiwi_menu.add(InlineKeyboardButton(text="🥝 Оплата через QIWI", callback_data="qiwi"))
    qiwi_menu.add(InlineKeyboardButton(text="₿ Оплата криптовалютой", callback_data="crypto"))
    return qiwi_menu


def get_subscribe_payment(url, translation: DbTranslation):
    qiwi_menu = InlineKeyboardMarkup()
    btn_url = InlineKeyboardButton(text=translation.go_payment_b, url=url)
    btn_accept = InlineKeyboardButton(
        # text="⌛️Я ОПЛАТИЛ", callback_data="accept_payment"  # todo 2/28/2022 6:15 PM taima:
        text=f"{translation.accept_payment_b}.",
        callback_data="accept_payment",  # todo 2/28/2022 6:15 PM taima:
    )
    btn_reject = InlineKeyboardButton(text=translation.reject_payment_b, callback_data="reject_payment")
    qiwi_menu.add(btn_url)
    qiwi_menu.add(btn_accept)
    qiwi_menu.add(btn_reject)
    return qiwi_menu


def get_subscribe_payment_api(url, translation: DbTranslation):
    qiwi_menu = InlineKeyboardMarkup()
    btn_url = InlineKeyboardButton(text=translation.go_payment_b, url=url)
    btn_accept = InlineKeyboardButton(
        # text="⌛️Я ОПЛАТИЛ", callback_data="accept_payment"  # todo 2/28/2022 6:15 PM taima:
        text=translation.accept_payment_b,
        callback_data="accept_payment_api",  # todo 2/28/2022 6:15 PM taima:
    )
    btn_reject = InlineKeyboardButton(text=translation.reject_payment_b, callback_data="reject_payment_api")
    qiwi_menu.add(btn_url)
    qiwi_menu.add(btn_accept)
    qiwi_menu.add(btn_reject)
    return qiwi_menu


def renew_subscription(title):  # todo 3/2/2022 3:21 PM taima:

    for pk, item in SUBSCRIPTIONS_INFO.items():
        if item.title == title:
            break
    else:
        return
    btn_renew = [[InlineKeyboardButton(text="Продлить подписку", callback_data=f"view_buy_{pk}")]]

    renew = InlineKeyboardMarkup(
        inline_keyboard=btn_renew
        # row_width=3
    )
    return renew


def renew_subscription_api(title):  # todo 3/2/2022 3:21 PM taima:

    for pk, item in SUBSCRIPTIONS_INFO_API.items():
        if item.title == title:
            break
    else:
        return
    btn_renew = [[InlineKeyboardButton(text="Продлить подписку", callback_data=f"view_buy_api_{pk}")]]

    renew = InlineKeyboardMarkup(
        inline_keyboard=btn_renew
        # row_width=3
    )
    return renew
