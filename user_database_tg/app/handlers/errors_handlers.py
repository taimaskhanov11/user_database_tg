from aiogram import Dispatcher
from loguru import logger


# logger = logging.getLogger(__name__)


async def error_handler(update, exception):
    # logger.exception(f"{exception}")
    logger.error(f"{exception}|{update}")
    # print(exception)
    return True


def register_error_handlers(dp: Dispatcher):
    dp.register_errors_handler(error_handler)
