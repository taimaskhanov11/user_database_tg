from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from loguru import logger

from user_database_tg.app.translation.message_translation import TRANSLATIONS
from user_database_tg.db.models import DbUser


class MainPaymentFilter(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        db_user = await DbUser.get_or_new(call.from_user.id, call.from_user.username)
        translation = TRANSLATIONS[db_user.language]
        return {"db_user": db_user, "translation": translation}


class ViewSubscriptionFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data.startswith("view_buy_"):
            return await super().check(call)


class SubscribeFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data.startswith("subscribe_"):
            return await super().check(call)


class RejectPaymentFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "reject_payment":
            return await super().check(call)


class AcceptPaymentFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "accept_payment":
            return await super().check(call)
