from _ast import In

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

btn_current_menu = InlineKeyboardButton(
    text="Посмотреть текущий перевод меню", callback_data="watch_translate"
)
btn_change_menu = InlineKeyboardButton(
    text="Изменить меню", callback_data="change_translate"
)

btn_change_price = InlineKeyboardButton(
    text="Изменить цены", callback_data="change_prices"
)


admin_menu = InlineKeyboardMarkup(inline_keyboard=[[]])
