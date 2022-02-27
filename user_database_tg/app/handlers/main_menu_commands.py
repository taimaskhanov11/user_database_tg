from aiogram import Dispatcher, types
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.translation.message_data import Translation


async def profile(message: types.Message, translation: Translation):
    await message.answer(translation.profile)  # todo 2/25/2022 12:34 AM taima:


@logger.catch
async def buy(message: types.Message, translation: Translation):
    await message.answer(translation.subscribe, reply_markup=markups.get_subscribe_menu(translation))


async def description(message: types.Message, translation: Translation):
    await message.answer(translation.description, reply_markup=markups.get_menu(translation))


async def support(message: types.Message, translation: Translation):
    await message.answer(translation.support, reply_markup=markups.get_menu(translation))


def register_main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(profile, text_startswith="👤")
    dp.register_message_handler(buy, text_startswith="💰")
    dp.register_message_handler(description, text_startswith="❗")
    dp.register_message_handler(support, text_startswith="🙋‍♂")
