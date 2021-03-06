from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from user_database_tg.app.markups import admin_menu
from user_database_tg.config.config import ADMINS
from user_database_tg.db.models import DbUser


async def admin_start(message: types.Message, db_user: DbUser, state: FSMContext):  # todo 2/27/2022 12:39 PM taima:
    await state.finish()
    await message.answer("Admin menu", reply_markup=admin_menu.admin_start)
    await message.answer("Выберите опцию", reply_markup=admin_menu.admin_menu_main)
    # сохранить последние изменения


async def no_admin_start(message: types.Message):
    await message.answer("Вы не администратор!")


async def bot_settings(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("Admin menu", reply_markup=admin_menu.menu)


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(
        admin_start,
        commands="admin_start",
        # is_chat_admin=[1985947355, 2014301618]
        user_id=ADMINS,
        state="*",
    )
    dp.register_callback_query_handler(bot_settings, text="bot_settings")
    dp.register_message_handler(
        no_admin_start,
        commands="admin_start",
        state="*",
    )
