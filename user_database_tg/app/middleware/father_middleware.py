from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from user_database_tg.db.models import User


class FatherMiddleware(BaseMiddleware):
    # 1
    # @logger.catch
    # async def on_pre_process_update(self, update: types.Update, data: dict):
    #     if update.callback_query:
    #         user = await User.get_or_new(update.callback_query.from_user.id, update.callback_query.from_user.username)
    #         data["user"] = user
    #         logger.critical(data)

    # 3
    async def on_process_message(self, message: types.Message, data: dict):
        logger.info(f"3.Pre Process Message, {data=}")
        user = await User.get_or_new(message.from_user.id, message.from_user.username)
        data["user"] = user
        # data["user"] = User.get_or_create(user_id=message.from_user.id, defaults={
        #
        # })
