from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class EditUserFilter(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data.startswith("edit_user_"):
            return True


class EditUserFilterAPI(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data.startswith("edit_user_api_"):
            return True
