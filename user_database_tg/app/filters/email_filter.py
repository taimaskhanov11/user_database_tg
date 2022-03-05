import re

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from loguru import logger


class EmailFilter(BoundFilter):
    async def check(self, message: types.Message):
        # data = ctx_data.get()
        # logger.info(f"4.Filter, {data=}")
        # if message.text[0].isalpha() and '@' in message.text:
        match = re.match(
            r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
            message.text.lower(),
        )
        # if "@" in message.text:
        logger.trace(match)
        if match:
            return True
        return False
        # return {"from_filter": "Данные из фильтра"}
