from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from user_database_tg.app.subscription.subscription_info import SUBSCRIPTIONS_INFO
from user_database_tg.app.translation.message_translation import Translation
from user_database_tg.db.models import DbTranslation


def get_subscribe_menu(translation: DbTranslation):
    btns_subscribe = [
        [InlineKeyboardButton(text=sub.title, callback_data=f"subscribe_{pk}")]
        for pk, sub in SUBSCRIPTIONS_INFO.items()
    ]

    # bnt_1_25 = InlineKeyboardButton(
    #     text="1 месяц [25 в сутки] - 35р", callback_data="subscribe_d1_25_1"
    # )  # todo 2/27/2022 12:19 PM taima:
    # bnt_1_100 = InlineKeyboardButton(
    #     text="1 месяц [100 запросов в сутки] - 100р", callback_data="subscribe_d1_100_1"
    # )
    # bnt_1_n = InlineKeyboardButton(
    #     text="1 месяц [Безлимит] - 500р", callback_data="subscribe_d1_n_1"
    # )
    #
    # bnt_6_25 = InlineKeyboardButton(
    #     text="6 месяц [25 в сутки] - 200р", callback_data="subscribe_d6_25_1"
    # )
    # bnt_6_100 = InlineKeyboardButton(
    #     text="6 месяц [100 в сутки] - 550р", callback_data="subscribe_d6_100_1"
    # )
    # bnt_6_n = InlineKeyboardButton(
    #     text="6 месяц [Безлимит] - 2700р", callback_data="subscribe_d6_n_1"
    # )
    #
    # bnt_12_25 = InlineKeyboardButton(
    #     text="12 месяц [25 в сутки] 350р", callback_data="subscribe_d12_25_1"
    # )
    # bnt_12_100 = InlineKeyboardButton(
    #     text="12 месяц(100 в сутки) 1000р", callback_data="subscribe_d12_100_1"
    # )
    # bnt_12_n = InlineKeyboardButton(
    #     text="12 месяц(Безлимит) 5000р", callback_data="subscribe_d12_n_1"
    # )

    # subscribe_menu = InlineKeyboardMarkup(
    #     inline_keyboard=[
    #         [bnt_1_25],
    #         [bnt_1_100],
    #         [bnt_1_n],
    #         [bnt_6_25],
    #         [bnt_6_100],
    #         [bnt_6_n],
    #         [bnt_12_25],
    #         [bnt_12_100],
    #         [bnt_12_n],
    #     ],
    #     # row_width=3
    # )
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
