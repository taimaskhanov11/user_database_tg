from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from loguru import logger

from user_database_tg.config.config import CHECKING_USERS


class BigDaddy(BaseMiddleware):
    # 1
    async def on_pre_process_update(self, update: types.Update, data: dict):
        logger.info(f"{'-' * 15}Новый апдейт{'-' * 15}")
        logger.info(f"1. Pre-process update")
        logger.info(f"Следующая точка: Process Update")
        data["middleware_data"] = "Это дойдет до on_post_process_update"
        if update.message:
            user = update.message.from_user.id
        elif update.callback_query:
            user = update.message.from_user.id
        else:
            return
        if user in CHECKING_USERS:
            raise CancelHandler

    # 2
    async def on_process_update(self, update: types.Update, data: dict):
        logger.info(f"2.Process Update, {data=}")

    # 3
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logger.info(f"3.Pre Process Message, {data=}")
        data["middleware_data"] = "Это пройдет в on_process_message"

    # 4 Filters

    # 5
    async def on_process_message(self, message: types.Message, data: dict):
        logger.info(f"5.On Process Message, {data=}")
        data["middleware_data"] = "Это попадет в хендлер"

    # 6 Handler

    # 7
    async def on_post_process_message(self, message: types.Message, data_from_handler: list, data: dict):
        logger.info(f"7.Post Process Message>, {data_from_handler}{data}")

    # 8
    async def on_post_process_update(self, update: types.Update, data_from_handler: list, data: dict):
        logger.info(f"8.Post Process Update, {data}")
        logger.info(f"End")


