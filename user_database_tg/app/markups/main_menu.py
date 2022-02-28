from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from user_database_tg.app.translation.message_translation import Translation

btn_ru = KeyboardButton("🇷🇺 Русский")
btn_eng = KeyboardButton("🇬🇧 English")
lang_choice = ReplyKeyboardMarkup([[btn_ru, btn_eng]], resize_keyboard=True)


def get_menu(translation: Translation):
    btn_prof = KeyboardButton(translation.profile_b)
    btn_buy = KeyboardButton(translation.subscribe_b)
    btn_des = KeyboardButton(translation.description_b)
    btn_supp = KeyboardButton(translation.support_b)
    menu = ReplyKeyboardMarkup(
        [[btn_prof, btn_buy, btn_des], [btn_supp]], resize_keyboard=True
    )
    return menu
