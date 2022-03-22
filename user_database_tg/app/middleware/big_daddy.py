from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger


class BigDaddy(BaseMiddleware):
    # 1
    async def on_pre_process_update(self, update: types.Update, data: dict):
        logger.info(f"{'-' * 15}Новый апдейт{'-' * 15}")
        logger.info(f"1. Pre-process update")
        logger.info(f"Следующая точка: Process Update")
        data["on_pre_process_update"] = "on_pre_process_update"

    # 2
    async def on_process_update(self, update: types.Update, data: dict):
        logger.info(f"2.Process Update, {data=}")
        data["on_process_update"] = "on_process_update"

    # 3
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logger.info(f"3.Pre Process Message, {data=}")
        data["on_pre_process_message"] = "on_pre_process_message"

    # 4 Filters

    # 5
    async def on_process_message(self, message: types.Message, data: dict):
        logger.info(f"5.On Process Message, {data=}")
        data["on_process_message"] = "on_process_message"

    # 6 Handler

    # 7
    async def on_post_process_message(self, message: types.Message, data_from_handler: list, data: dict):
        logger.info(f"7.Post Process Message>, {data_from_handler}{data}")
        data["on_post_process_message"] = "on_post_process_message"

    # 8
    async def on_post_process_update(self, update: types.Update, data_from_handler: list, data: dict):
        logger.info(f"8.Post Process Update, {data}")
        logger.info(f"End")
