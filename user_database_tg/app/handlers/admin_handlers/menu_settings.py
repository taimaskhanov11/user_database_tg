from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from user_database_tg.app.markups.admin_menu import MENU_FIELDS
from user_database_tg.app.translation.google_translation import translate
from user_database_tg.app.translation.message_translation import (
    TRANSLATIONS,
    init_english,
)


class EditMenuField(StatesGroup):
    start = State()
    end = State()


async def view_menu(call: types.CallbackQuery):
    rus = TRANSLATIONS.get("russian")
    await call.message.answer(
        f"В ответном сообщении отправьте цифру поля, которую хотите изменить."
        f" Для отмены введите /start \n\n{rus}"
    )
    await EditMenuField.first()


async def edit_menu_field_start(message: types.Message, state: FSMContext):
    field_number = message.text
    if field_number.isdigit():
        await state.update_data(field_number=int(field_number))

        await message.answer(
            f"Ведите новое значение для поля {MENU_FIELDS[int(field_number)]}"
        )
        await EditMenuField.next()

    else:
        await message.answer("Ведите цифру. Для отмены введите /admin_start")


async def edit_menu_field_end(message: types.Message, state: FSMContext):
    data = await state.get_data()
    field_number = data["field_number"]
    ru = TRANSLATIONS["russian"]
    setattr(ru, MENU_FIELDS[field_number], message.text)
    await ru.save()
    # await init_english()
    en = TRANSLATIONS["english"]
    en_trans_data = await translate(MENU_FIELDS[field_number], message.text)
    setattr(en, MENU_FIELDS[field_number], en_trans_data[MENU_FIELDS[field_number]])
    await en.save()
    await message.answer(
        "Данные обновлены. Перевод на английский переведен автоматически"
    )
    await state.finish()


def register_menu_settings_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(view_menu, text="view_menu")
    dp.register_message_handler(edit_menu_field_start, state=EditMenuField.start)
    dp.register_message_handler(edit_menu_field_end, state=EditMenuField.end)
