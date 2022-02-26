from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.messages.menu import START_MESSAGE
from user_database_tg.db.models import DbUser


class LangChoice(StatesGroup):
    start = State()


@logger.catch
async def start(message: types.Message, state: FSMContext, db_user: DbUser):
    await state.finish()
    if not db_user.language:
        await message.answer("Выберите предпочитаемый язык\nChoose your preferred language",
                             reply_markup=markups.lang_choice)
        await LangChoice.first()
    await message.answer(START_MESSAGE, reply_markup=markups.menu)


async def lang_choice(message: types.Message, state: FSMContext, db_user: DbUser):  # todo 2/24/2022 11:41 PM taima:
    if message.text.startswith("🇷🇺"):
        await message.answer("Язык интерфейса выбран 🇷🇺", reply_markup=markups.menu)
        db_user.language = "russian"
    elif message.text.startswith("🇬🇧"):
        await message.answer("The interface language is selected 🇬🇧", reply_markup=markups.menu)
        db_user.language = "english"
    else:
        await message.answer("Нажмите на соответствующую кнопку\nClick on the corresponding button",
                             reply_markup=markups.lang_choice)
        return

    await db_user.save()
    await state.finish()


def register_common_handlers(dp: Dispatcher):
    # dp.register_message_handler(start_for_unknown, lambda m: m.from_user.id not in users, commands="start", state="*")
    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(lang_choice, state=LangChoice.start)
