from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bnt_one_day = InlineKeyboardButton(text="Подписка на день (3 руб)", callback_data="subscribe_day")
bnt_month = InlineKeyboardButton(text="Подписка на месяц (10 руб)", callback_data="subscribe_month")
subscribe_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [bnt_one_day, bnt_month]
    ]
)


def get_subscribe(url):
    qiwi_menu = InlineKeyboardMarkup()
    btn_url = InlineKeyboardButton(text="Перейти к оплате", url=url)
    qiwi_menu.add(btn_url)
    return qiwi_menu
