from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from loguru import logger


class EmailFilter(BoundFilter):

    async def check(self, message: types.Message):
        # data = ctx_data.get()
        # logger.info(f"4.Filter, {data=}")
        # if message.text[0].isalpha() and '@' in message.text:
        if '@' in message.text:
            return True
        return False
        # return {"from_filter": "Данные из фильтра"}
