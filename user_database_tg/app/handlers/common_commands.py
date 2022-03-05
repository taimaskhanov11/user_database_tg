from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.translation.message_translation import (
    TRANSLATIONS,
)
from user_database_tg.db.models import DbUser, DbTranslation


class LangChoice(StatesGroup):
    start = State()


@logger.catch
async def start(
    message: types.Message,
    state: FSMContext,
    db_user: DbUser,
    translation: DbTranslation,
):
    await state.finish()
    if not db_user.language:
        await message.answer(
            "Выберите предпочитаемый язык\nChoose your preferred language",
            reply_markup=markups.lang_choice,
        )
        await LangChoice.first()
        return
    await message.answer(
        translation.start_message, reply_markup=markups.get_menu(translation)
    )


async def lang_choice(
    message: types.Message, state: FSMContext, db_user: DbUser
):  # todo 2/24/2022 11:41 PM taima:
    if message.text.startswith("🇷🇺"):
        db_user.language = "russian"
        translation = TRANSLATIONS[db_user.language]
        await message.answer(
            "Язык интерфейса выбран 🇷🇺 ✅", reply_markup=markups.get_menu(translation)
        )

    elif message.text.startswith("🇬🇧"):
        db_user.language = "english"
        translation = TRANSLATIONS[db_user.language]
        await message.answer(
            "The interface language is selected 🇬🇧 ✅",
            reply_markup=markups.get_menu(translation),
        )
    else:
        await message.answer(
            "Нажмите на соответствующую кнопку\nClick on the corresponding button",
            reply_markup=markups.lang_choice,
        )
        return

    await db_user.save()
    await state.finish()


def register_common_handlers(dp: Dispatcher):
    # dp.register_message_handler(start_for_unknown, lambda m: m.from_user.id not in users, commands="start", state="*")
    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(lang_choice, state=LangChoice.start)
