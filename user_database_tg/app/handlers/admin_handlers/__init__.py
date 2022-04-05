from aiogram import Dispatcher

from .admin_panel import register_admin_menu_handlers
from .bot_settings import register_bot_info_handler
from .menu_settings import register_menu_settings_handlers
from .subscription_settings import register_admin_subscription_settings_handlers


def register_admin_handlers(dp: Dispatcher):
    register_admin_menu_handlers(dp)
    register_admin_subscription_settings_handlers(dp)
    register_menu_settings_handlers(dp)
    register_bot_info_handler(dp)
