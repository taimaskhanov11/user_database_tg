from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class ChangeSubscriptionInfoStart(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data in ["title", "days", "daily_limit", "price"]:
            return True
