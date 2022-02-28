import datetime

from aiogram import Dispatcher, types
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.translation.message_translation import Translation
from user_database_tg.config.config import TZ
from user_database_tg.db.models import DbUser, DbTranslation


async def profile(
    message: types.Message, db_user: DbUser, translation: DbTranslation
):  # todo 2/25/2022 12:34 AM taima:
    await message.answer(
        translation.profile.format(
            user_id=db_user.user_id,
            username=db_user.username,
            remaining_daily_limit=db_user.subscription.remaining_daily_limit,
            sub=db_user.subscription.title,
            duration=db_user.subscription.duration - datetime.datetime.now(TZ)
            if db_user.subscription.is_subscribe
            else 0,
        )
    )


@logger.catch
async def buy(message: types.Message, translation: DbTranslation):
    await message.answer(
        translation.subscribe, reply_markup=markups.get_subscribe_menu(translation)
    )


async def description(message: types.Message, translation: DbTranslation):
    await message.answer(
        translation.description, reply_markup=markups.get_menu(translation)
    )


async def support(message: types.Message, translation: DbTranslation):
    await message.answer(
        translation.support, reply_markup=markups.get_menu(translation)
    )


def register_main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(profile, text_startswith="👤")
    dp.register_message_handler(buy, text_startswith="💳")
    dp.register_message_handler(description, text_startswith="🗒")
    dp.register_message_handler(support, text_startswith="🙋‍♂")
