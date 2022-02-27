from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from user_database_tg.app.translation.message_data import translations
from user_database_tg.db.models import DbUser


class FatherMiddleware(BaseMiddleware):
    # 1
    # @logger.catch
    # async def on_pre_process_update(self, update: types.Update, data: dict):
    #     if update.callback_query:
    #         user = await User.get_or_new(update.callback_query.from_user.id, update.callback_query.from_user.username)
    #         data["user"] = user
    #         logger.critical(data)

    # async def on_process_update(self, update: types.Update, data: dict):
    #     logger.info(f"2.Process Update, {data=}")
    #     data["on_process_update"] = "on_process_update"
    #
    # async def on_pre_process_message(self, message: types.Message, data: dict):
    #     logger.info(f"3.Pre Process Message, {data=}")
    #     data["on_pre_process_message"] = "on_pre_process_message"


    # 3
    async def on_process_message(self, message: types.Message, data: dict):
        logger.info(f"3.Process Message, {data=}")
        db_user = await DbUser.get_or_new(message.from_user.id, message.from_user.username)
        data["db_user"] = db_user
        data["translation"] = translations.get(db_user.language)
        logger.info(repr(db_user))
        # data["user"] = User.get_or_create(user_id=message.from_user.id, defaults={
        #
        # })
