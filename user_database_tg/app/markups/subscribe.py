from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_subscribe_menu(wait=False):
    if wait:
        btn_cancel = InlineKeyboardButton("Отменить предыдущую оплату", callback_data='reject_payment')
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [btn_cancel],

            ],
            row_width=1
        )

    bnt_1_25 = InlineKeyboardButton(text="1 мес(25 в сутки) 35р", callback_data="subscribe_d1_25_35")
    bnt_1_100 = InlineKeyboardButton(text="1 мес(100 в сутки) 100р", callback_data="subscribe_d1_100_100")
    bnt_1_n = InlineKeyboardButton(text="1 мес(Безлимит) 500р", callback_data="subscribe_d1_n_500")

    bnt_6_25 = InlineKeyboardButton(text="6 мес(25 в сутки) 200р", callback_data="subscribe_d6_25_200")
    bnt_6_100 = InlineKeyboardButton(text="6 мес(100 в сутки) 550р", callback_data="subscribe_d6_100_550")
    bnt_6_n = InlineKeyboardButton(text="6 мес(Безлимит) 2700р", callback_data="subscribe_d6_n_2700")

    bnt_12_25 = InlineKeyboardButton(text="12 мес(25 в сутки) 350р", callback_data="subscribe_d12_25_350")
    bnt_12_100 = InlineKeyboardButton(text="12 мес(100 в сутки) 1000р", callback_data="subscribe_d12_100_1000")
    bnt_12_n = InlineKeyboardButton(text="12 мес(Безлимит) 5000р", callback_data="subscribe_d12_n_5000")

    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [bnt_1_25, bnt_1_100],
            [bnt_1_n],
            [bnt_6_25, bnt_6_100],
            [bnt_6_n],
            [bnt_12_25, bnt_12_100],
            [bnt_12_n],
        ],
        # row_width =3

    )
    return subscribe_menu


def get_subscribe(url):
    qiwi_menu = InlineKeyboardMarkup()
    btn_url = InlineKeyboardButton(text="Перейти к оплате", url=url)
    qiwi_menu.add(btn_url)
    return qiwi_menu
