from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

btn_ru = KeyboardButton("🇷🇺 Русский")
btn_eng = KeyboardButton("🇬🇧 English")
lang_choice = ReplyKeyboardMarkup(
    [[btn_ru, btn_eng]],
    resize_keyboard=True
)

btn_prof = KeyboardButton("👤 Профиль")
btn_buy = KeyboardButton("🗂 Купить")
btn_des = KeyboardButton("👉 Описание")
btn_supp = KeyboardButton("🙋‍♂️ Поддержка")
menu = ReplyKeyboardMarkup(
    [[btn_prof, btn_buy, btn_des],
     [btn_supp]],
    resize_keyboard=True
)
