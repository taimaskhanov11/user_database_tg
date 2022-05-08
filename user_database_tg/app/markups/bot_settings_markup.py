from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_edit_user(user_id):
    current_sub_info = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить данные подписки",
                    callback_data=f"edit_user_{user_id}",
                )
            ]
        ]
    )
    return current_sub_info


def get_edit_user_api(user_id):
    current_sub_info = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить данные подписки",
                    callback_data=f"edit_user_api_{user_id}",
                )
            ]
        ]
    )
    return current_sub_info


channel_status_data = [
    ("Изменить статус", "change_sub_status"),
    ("Изменить группу или канал подписки", "change_sub_channel"),
]

channel_status = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=text,
                callback_data=data,
            )
        ]
        for text, data in channel_status_data
    ]
)
