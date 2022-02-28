from _ast import In

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

admin_menu_data = [
    ("Посмотреть подписки", "view_subscription"),
    ("Создать новую подписку", "create_subscription"),
]
kbr_admin_menu = [
    [
        InlineKeyboardButton(
            text=text,
            callback_data=data,
        )
    ]
    for text, data in admin_menu_data
]

menu = InlineKeyboardMarkup(inline_keyboard=kbr_admin_menu)
