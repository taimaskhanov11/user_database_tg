from aiogram import Dispatcher, types
from loguru import logger

from user_database_tg.app.filters.email_filter import EmailFilter
from user_database_tg.app.translation.message_data import Translation
from user_database_tg.db.models import *
from user_database_tg.db.models import DbUser


async def search_data(message: types.Message, db_user: DbUser, translation: Translation):
    # logger.critical(db_user)
    # logger.info("6.Handler")
    # logger.debug(middleware_data)
    # logger.debug(from_filter)



    if db_user.is_search:
        await message.answer(translation.wait_search)
        return
    db_user.is_search = True
    await db_user.save()
    sign = message.text[0]

    if sign.isalpha():
        hack_model = globals()[f"{sign}_HackedUser"]
    elif sign.isdigit():
        hack_model = globals()[f"dig_file_HackedUser"]
    else:
        hack_model = globals()[f"sym_file_HackedUser"]

    logger.debug(f"Поиск {message.text} в таблице {hack_model.__name__}")
    res = await hack_model.filter(email=message.text)
    if not res:
        await message.answer(translation.data_not_found)
    else:
        answer = ''.join([f"{h.email}|{h.password}|{h.service}\n" for h in res])
        await message.answer(answer)
    db_user.is_search = False
    await db_user.save()


def register_data_search_handlers(dp: Dispatcher):
    # dp.register_message_handler(search_data, lambda m: m.text[0].isalpha() and "@" in m.text)
    dp.register_message_handler(search_data, EmailFilter())