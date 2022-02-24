from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from user_database_tg.app import markups
from user_database_tg.app.messages.menu import START_MESSAGE

users = []  # todo 2/24/2022 11:26 PM taima:


class LangChoice(StatesGroup):
    start = State()


async def start_for_unknown(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Выберите предпочитаемый язык\nChoose your preferred language",
                         reply_markup=markups.lang_choice)
    await LangChoice.first()


async def start_for_known(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(START_MESSAGE, reply_markup=markups.menu)


async def lang_choice(message: types.Message, state: FSMContext):  # todo 2/24/2022 11:41 PM taima:
    if message.text.startswith("🇷🇺"):
        await message.answer("Язык интерфейса выбран", reply_markup=markups.menu)
    elif message.text.startswith("🇬🇧"):
        await message.answer("The interface language is selected", reply_markup=markups.menu)
    else:
        await message.answer("Нажмите на соответствующую кнопку\nClick on the corresponding button",
                             reply_markup=markups.lang_choice)
        return
    users.append(message.from_user.id)  # todo 2/24/2022 11:50 PM taima:
    await state.finish()


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(start_for_unknown, lambda m: m.from_user.id not in users, commands="start", state="*")
    dp.register_message_handler(start_for_known, commands="start", state="*")
    dp.register_message_handler(lang_choice, state=LangChoice.start)
