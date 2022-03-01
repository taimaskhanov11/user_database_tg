from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from user_database_tg.app import subscription
from user_database_tg.app.subscription.subscription_info import SUBSCRIPTIONS_INFO

admin_menu_main_data = [
    ("Общая информация о боте", "bot_info"),
    ("Информация о конкретном пользователе", "user_info"),
    ("Настройка работы бота", "bot_settings"),
]

admin_menu_main = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=data,
                )
            ]
            for text, data in admin_menu_main_data
        ]
    )

admin_menu_data = [
    ("Посмотреть подписки", "view_all_subscriptions"),
    ("Создать новую подписку", "create_subscription"),
    ("Посмотреть меню", "view_menu"),
    ("Настроить подписку на канал/группу", "sub_channel_status"),
    # todo 3/1/2022 10:26 PM taima:
]
btn_admin_menu = [
    [
        InlineKeyboardButton(
            text=text,
            callback_data=data,
        )
    ]
    for text, data in admin_menu_data
]
menu = InlineKeyboardMarkup(inline_keyboard=btn_admin_menu)


# ********************
# create subscription
class KBRSubscriptionField:
    days = ReplyKeyboardMarkup(
        [["10", "30", "45"]],
        resize_keyboard=True
    )

    daily_limit = ReplyKeyboardMarkup(
        [["20", "100", "Unlimited"]],
        resize_keyboard=True
    )

    price = ReplyKeyboardMarkup(
        [["100", "500", "1500"]],
        resize_keyboard=True
    )


# ******************

def get_current_sub_info():
    current_sub_info = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=sub_info.title,
                    callback_data=f"view_subscription_{pk}",
                )
            ]
            for pk, sub_info in SUBSCRIPTIONS_INFO.items()
        ]
    )
    return current_sub_info


change_field = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=title,
                callback_data=field,
            )
        ]
        for title, field in (
            ("Изменить название", "title"),
            ("Изменить длительность подписки", "days"),
            ("Изменить дневной лимит", "daily_limit"),
            ("Изменить цену", "price"),
        )
    ]
)

MENU_FIELDS = {
    1: "start_message",
    2: "profile",
    3: "description",
    4: "support",
    5: "subscribe",
    6: "profile_b",
    7: "description_b",
    8: "support_b",
    9: "subscribe_b",
    10: "wait_search",
    11: "data_not_found",
    12: "daily_limit_ended",
    13: "left_attempts",
    14: "create_payment",
    15: "wait_payment",
    16: "go_payment_b",
    17: "payment_not_found",
    18: "accept_payment",
    19: "accept_payment_b",
    20: "reject_payment",
    21: "reject_payment_b",
}
