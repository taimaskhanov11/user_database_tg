import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot
from aiogram.types import BotCommand
from loguru import logger as log

from user_database_tg.api.server import get_server_host
from user_database_tg.app.filters.email_filter import EmailFilter
from user_database_tg.app.handlers import (
    register_admin_menu_handlers,
    register_common_handlers,
    register_data_search_handlers,
    register_main_menu_handlers,
    register_subscriptions_handlers,
)
from user_database_tg.app.handlers.admin_handlers import (
    register_admin_handlers,
)
from user_database_tg.app.handlers.api_handlers import register_api_handlers
from user_database_tg.app.handlers.errors_handlers import register_error_handlers
from user_database_tg.app.handlers.make_api_subscription import register_subscriptions_api_handlers
from user_database_tg.app.middleware.father_middleware import FatherMiddleware
from user_database_tg.app.subscription.subscription_info import init_subscriptions_info
from user_database_tg.app.translation.message_translation import init_translations
from user_database_tg.app.utils.daily_processes import (
    everyday_processes,
)
from user_database_tg.app.utils.sub_channel import init_sub_channel
from user_database_tg.config.config import BASE_DIR
from user_database_tg.db.db_main import init_db
from user_database_tg.db.utils.backup import making_backup
from user_database_tg.loader import bot, dp

log.remove()

log.add(
    sink=sys.stderr,
    # level="TRACE",
    level="INFO",
    enqueue=True,
    diagnose=True,
)

log.add(
    sink=Path(BASE_DIR, "logs/main.log"),
    level="TRACE",
    enqueue=True,
    encoding="utf-8",
    diagnose=True,
    rotation="5MB",
    compression="zip",
)

logging.basicConfig(
    encoding="utf-8",
    level=logging.INFO,
    handlers=[
        # logging.StreamHandler(),
        logging.FileHandler(filename=Path(BASE_DIR, "logs/aiolog.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# Регистрация команд, отображаемых в интерфейсе Telegram
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Главное меню"),
        BotCommand(command="/admin_start", description="Главное меню для админов"),
        # BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():

    # Получение сервер для API
    asyncio.create_task(get_server_host())

    log.info("Starting bot")
    # Парсинг файла конфигурации
    # config = load_config("config/bot.ini")
    # Объявление и инициализация объектов бота и диспетчера
    # bot = Bot(token=TG_TOKEN)
    # dp = Dispatcher(bot, storage=MemoryStorage())
    print((await bot.get_me()).username)

    # Меню админа
    register_admin_handlers(dp)

    # Регистрация хэндлеров
    register_common_handlers(dp)
    register_api_handlers(dp)
    register_subscriptions_api_handlers(dp)

    register_main_menu_handlers(dp)
    register_subscriptions_handlers(dp)
    register_admin_menu_handlers(dp)
    register_data_search_handlers(dp)

    register_error_handlers(dp)
    # Регистрация middleware
    # dp.middleware.setup(ThrottlingMiddleware(3))
    # dp.middleware.setup(BigDaddy())
    dp.middleware.setup(FatherMiddleware())
    # router = Router()
    # dp.middleware.setup(CounterMiddleware())
    # dp.middleware.setup(LoggingMiddleware())
    # dp.middleware.setup(ThrottlingMiddleware(5))

    # Регистрация фильтров
    dp.filters_factory.bind(EmailFilter)

    # Установка команд бота
    await set_commands(bot)

    # Инициализация базы данных
    await init_db()

    # Инициализация переводов
    await init_translations()

    # Инициализация информации подписок
    await init_subscriptions_info()

    await init_sub_channel()

    # Запуск задачи ежедневного обновления запросов и проверки подписки
    asyncio.create_task(everyday_processes())

    # Создание ежедневного резервного копирования
    asyncio.create_task(making_backup(3600))

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
