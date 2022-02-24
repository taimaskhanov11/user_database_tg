from aiogram import Dispatcher, types

from user_database_tg.app import markups


async def profile(message: types.Message):
    await message.answer(f"🔑 ID: {message.from_user.id}\n"
                         f"👤 Логин: {message.from_user.username}\n"
                         f"🕜 Всего запросов до 00ч. 00мин. МСК: 10.")  # todo 2/25/2022 12:34 AM taima:


async def buy(message: types.Message):
    await message.answer("Выберите подписку", reply_markup=markups.subscribe_menu)


async def description(message: types.Message):
    pass


async def support(message: types.Message):
    pass



def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(profile, text="👤 Профиль")
    dp.register_message_handler(buy, text="🗂 Купить")
    dp.register_message_handler(description, text="👉 Описание")
    dp.register_message_handler(support, text="🙋‍♂️ Поддержка")

