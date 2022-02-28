from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from user_database_tg.db.models import DbUser


class CreateSubscriptionState(StatesGroup):
    start = State()


async def admin_start(message: types.Message, db_user: DbUser, state: FSMContext):  # todo 2/27/2022 12:39 PM taima:
    await state.finish()
    await message.answer("Меню админа")
    # сохранить последние изменения


async def create_subscription_start(call: types.CallbackQuery):
    await CreateSubscriptionState.first()
    await call.message.answer(f"Введите данные подписки каждый с новой строки\n"
                              f"1. Описание которое будет отображаться на кнопке (не более 255 символов). Ни на что не вляет\n"
                              f"2. Длительность подписки в днях\n"
                              f"3. Количество запросов в день (или None чтобы сделать Анлим)\n"
                              f"4. Цену за длительность подписки\n"
                              f"Примеры:\n"
                              f"1 месяц 25 запросов в сутки,  100 рублей\n30\n25\n200\n"
                              f"Еще пример:\n"
                              f"Безлимитная подписка\n1000\nNone\n99999\n")


async def create_subscription_end(message: types.Message):
    try:
        title, days, daily_limit, price = message.text.split("\n")
        #todo 2/28/2022 8:00 PM taima: '
        await message.answer("Подписка успешно добавлена\nЧтобы сохранить все последние"
                             " выберите 'Сохранить изменения' в Главном меню")
    except Exception as e:
        logger.warning(e)
        await message.answer("Проверьте правильность веденных данных")



async def change_prices(message: types.Message):
    pass


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(
        admin_start,
        commands="admin_start",
        # is_chat_admin=[1985947355, 2014301618]
        user_id=[1985947355, 2014301618],
        state="*"
    )
    # dp.callback_query_handlers(
    #     change_prices
    # )
