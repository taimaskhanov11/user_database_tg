from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from user_database_tg.db.models import DbTranslation

btn_ru = KeyboardButton("🇷🇺 Русский")
btn_eng = KeyboardButton("🇬🇧 English")
lang_choice = ReplyKeyboardMarkup([[btn_ru, btn_eng]], resize_keyboard=True)


def get_menu(translation: DbTranslation):
    btn_prof = KeyboardButton(translation.profile_b)
    btn_api = KeyboardButton("🛠 API")
    btn_buy = KeyboardButton(translation.subscribe_b)
    btn_des = KeyboardButton(translation.description_b)
    btn_supp = KeyboardButton(translation.support_b)
    menu = ReplyKeyboardMarkup([[btn_prof, btn_buy, btn_des], [btn_api, btn_supp]], resize_keyboard=True)
    return menu


def get_add_info(add_info, is_hash):
    add_info_k = InlineKeyboardMarkup()
    if add_info:
        add_info_k.add(InlineKeyboardButton(
            text="Доп. информация по почте",
            callback_data="add_info",
        ))
    if is_hash:
        add_info_k.add(InlineKeyboardButton(
            text="Расшифровать хеши",
            callback_data="decrypt_hash",
        ))
    return add_info_k
