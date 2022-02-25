from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from user_database_tg.config.config import TG_TOKEN

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
