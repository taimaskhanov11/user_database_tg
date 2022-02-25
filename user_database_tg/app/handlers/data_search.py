from aiogram import Dispatcher, types
from loguru import logger

from user_database_tg.app.filters.email_filter import EmailFilter
from user_database_tg.config.config import CHECKING_USERS
from user_database_tg.db.models import *
from user_database_tg.db.models import User


async def search_data(message: types.Message, user:User):
    logger.critical(user)
    # logger.info("6.Handler")
    # logger.debug(middleware_data)
    # logger.debug(from_filter)
    user_id = message.from_user.id
    if user_id in CHECKING_USERS:
        await message.answer("Идет поиск предыдущего запроса пожалуйста ожидайте")
        return
    CHECKING_USERS.append(user_id)
    sign = message.text[0]
    hack_model = globals()[f"{sign}_HackedUser"]
    logger.debug(f"Поиск {message.text} в таблице {hack_model.__name__}")
    res = await hack_model.filter(email=message.text)
    if not res:
        await message.answer(f"Данных не найдено")
    else:
        answer = ''.join([f"{h.email}|{h.password}|{h.service}\n" for h in res])
        await message.answer(answer)
    CHECKING_USERS.remove(user_id)

def register_data_search(dp: Dispatcher):
    # dp.register_message_handler(search_data, lambda m: m.text[0].isalpha() and "@" in m.text)
    dp.register_message_handler(search_data, EmailFilter())
