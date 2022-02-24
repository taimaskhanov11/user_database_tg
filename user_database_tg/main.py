import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils import executor
from loguru import logger as log

from user_database_tg.app.handlers.main_menu_commands import register_main_menu
from user_database_tg.app.handlers.make_subscription import register_handlers_subscriptions
from user_database_tg.config.config import TG_TOKEN
from user_database_tg.app.handlers.common_commands import register_handlers_common

log.remove()
log.add(sink=sys.stderr, level='DEBUG', enqueue=True, diagnose=True, )
log.add(sink=f"../logs/paylog.log", level='TRACE', enqueue=True, encoding='utf-8', diagnose=True, )

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(filename="../logs/aiolog.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


# Регистрация команд, отображаемых в интерфейсе Telegram

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Hello world!"),
        # BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    # )
    logger.error("Starting bot")

    # Парсинг файла конфигурации
    # config = load_config("config/bot.ini")

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    print((await bot.get_me()).username)

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_main_menu(dp)
    register_handlers_subscriptions(dp)
    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
