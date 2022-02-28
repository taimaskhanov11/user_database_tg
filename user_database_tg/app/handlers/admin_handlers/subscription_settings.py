from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from user_database_tg.app.subscription.subscription_info import SUBSCRIPTIONS_INFO
from user_database_tg.db.models import DbUser, SubscriptionInfo


class CreateSubscriptionState(StatesGroup):
    start = State()
    title = State()


async def view_subscription(call: types.CallbackQuery):
    subscription_info = ""
    for pk, sub_info in SUBSCRIPTIONS_INFO.items():
        subscription_info += f"{sub_info}\n"
    await call.message.answer(f"Текущие подписки:\n{subscription_info}")


async def create_subscription_start(call: types.CallbackQuery):
    await CreateSubscriptionState.first()
    await call.message.answer(
        f"Введите данные подписки каждый с новой строки\n"
        f"1. Описание которое будет отображаться на кнопке (не более 255 символов). Ни на что не вляет\n"
        f"2. Длительность подписки в днях\n"
        f"3. Количество запросов в день (или None чтобы сделать Анлим)\n"
        f"4. Цену за длительность подписки\n"
        f"Примеры:\n"
        f"1 месяц 25 запросов в сутки,  100 рублей\n30\n25\n200\n"
        f"Еще пример:\n"
        f"Безлимитная подписка\n1000\nNone\n99999\n"
    )


async def create_subscription_title(message: types.Message):
    pass


async def create_subscription_title(message: types.Message):
    pass


async def create_subscription_title(message: types.Message):
    pass


async def create_subscription_title(message: types.Message):
    pass


async def create_subscription_end(message: types.Message, state: FSMContext):
    try:
        title, days, daily_limit, price = message.text.split("\n")
        # todo 2/28/2022 8:00 PM taima: '
        new_sub_info = await SubscriptionInfo.create(
            title=title, days=days, daily_limit=daily_limit, price=price
        )
        SUBSCRIPTIONS_INFO[new_sub_info.pk] = new_sub_info
        await message.answer(
            f"Подписка {new_sub_info.title} успешно добавлена\nЧтобы сохранить все последние"
            " выберите 'Сохранить изменения' в Главном меню"
        )
        await state.finish()
    except Exception as e:
        logger.warning(e)
        await message.answer("Проверьте правильность веденных данных")


async def change_prices(message: types.Message):
    pass


def register_admin_subscription_settings_handlers(dp: Dispatcher):
    # user_id = [1985947355, 2014301618]
    dp.register_callback_query_handler(view_subscription, text="view_subscription")
    dp.register_callback_query_handler(
        create_subscription_start, text="create_subscription"
    )
    dp.register_message_handler(
        create_subscription_end, state=CreateSubscriptionState.start
    )
