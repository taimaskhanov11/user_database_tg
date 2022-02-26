from aiogram import types, Dispatcher

from user_database_tg.db.models import DbUser


async def admin_start(message: types.Message, db_user: DbUser):

    await message.answer("Меню админа")


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(
        admin_start,
        commands="admin_start",
        # is_chat_admin=[1985947355, 2014301618]
        user_id=[1985947355, 2014301618]
    )

