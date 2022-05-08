from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from user_database_tg.app import markups
from user_database_tg.app.translation.message_translation import TRANSLATIONS
from user_database_tg.db.models import DbUser


async def api(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Сайт", reply_markup=markups.api.get_api_menu())


async def buy(call: types.CallbackQuery):
    translation = TRANSLATIONS.get("russian")
    await call.message.answer(translation.subscribe, reply_markup=markups.get_subscribe_menu_view_api())


async def get_token(call: types.CallbackQuery):
    db_user: DbUser = await DbUser.get_or_new(user_id=call.from_user.id, username=call.from_user.username)
    if db_user.api_subscription:
        if db_user.api_subscription.days_duration:
            await call.message.answer(f"Ваш текущий токен: {db_user.api_subscription.token}")
            return
    await call.message.answer(f"Нет активной подписки")


async def profile(
        call: types.CallbackQuery,
):
    db_user: DbUser = await DbUser.get_or_new(user_id=call.from_user.id, username=call.from_user.username)
    translation = TRANSLATIONS.get(db_user.language, "russian")

    answer = f"API Профиль\n"
    answer += translation.profile.format(
        user_id=db_user.user_id,
        username=db_user.username,
        remaining_daily_limit="Unlimited",
        sub=db_user.api_subscription.title,
        # duration=f"{duration.days} {duration.days}:{duration.hours}:{duration.minutes}"
        duration=f"\nДо окончания осталось дней: {db_user.api_subscription.days_duration}"
        if db_user.api_subscription.is_subscribe
        else ""
        # if db_user.subscription.is_subscribe
        # else 0,
    )
    await call.message.answer(
        answer,
        reply_markup=markups.renew_subscription_api(db_user.api_subscription.title)
        if db_user.api_subscription.daily_limit
        else None,
    )


def register_api_handlers(dp: Dispatcher):
    callback = dp.register_callback_query_handler
    message = dp.register_message_handler
    message(api, text_startswith="🛠")
    callback(buy, text="buy_api")
    callback(profile, text="api_profile")
    callback(get_token, text="get_token")
