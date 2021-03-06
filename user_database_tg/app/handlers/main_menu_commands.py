from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.db.models import DbUser, DbTranslation


async def profile(
        message: types.Message, db_user: DbUser, translation: DbTranslation, state:FSMContext
):  # todo 2/25/2022 12:34 AM taima:

    # duration: datetime.timedelta = db_user.subscription.duration - datetime.datetime.now(TZ)
    await state.finish()
    await message.answer(
        translation.profile.format(
            user_id=db_user.user_id,
            username=db_user.username,
            remaining_daily_limit=db_user.subscription.remaining_daily_limit
            if db_user.subscription.remaining_daily_limit is not None
            else "Unlimited",
            sub=db_user.subscription.title,
            # duration=f"{duration.days} {duration.days}:{duration.hours}:{duration.minutes}"
            duration=f"\nДо окончания осталось дней: {db_user.subscription.days_duration}"
            if db_user.subscription.is_subscribe
            else ""
            # if db_user.subscription.is_subscribe
            # else 0,
        ),
        reply_markup=markups.renew_subscription(db_user.subscription.title)
        if db_user.subscription.daily_limit
        else None,
    )


@logger.catch
async def buy(message: types.Message, translation: DbTranslation):
    await message.answer(translation.subscribe, reply_markup=markups.get_subscribe_menu_view())


async def description(message: types.Message, translation: DbTranslation):
    await message.answer(translation.description, reply_markup=markups.get_menu(translation))


async def support(message: types.Message, translation: DbTranslation):
    await message.answer(translation.support, reply_markup=markups.get_menu(translation))


def register_main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(profile, text_startswith="👤", state="*")
    dp.register_message_handler(buy, text_startswith="💳", state="*")
    dp.register_message_handler(description, text_startswith="🗒", state="*")
    dp.register_message_handler(support, text_startswith="🙋‍♂", state="*")
