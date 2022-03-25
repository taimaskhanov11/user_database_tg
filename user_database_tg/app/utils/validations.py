from loguru import logger

from user_database_tg.config.config import TempData
from user_database_tg.loader import bot


async def channel_status_check(user_id):
    chat_id = f"@{TempData.SUB_CHANNEL}"
    logger.trace(chat_id)
    try:
        status = await bot.get_chat_member(
            # chat_id=-1001790098718,
            chat_id=chat_id,
            # user_id=1985947355,
            user_id=user_id,
        )
        logger.trace(status)
        if status["status"] != "left":
            return True
        return False

    except Exception as e:
        logger.critical(e)
        return True


async def is_subscribe_to_channel(message, db_user, translation):
    if TempData.SUB_CHANNEL:
        if TempData.SUB_CHANNEL.checking:
            if not db_user.subscription.is_subscribe:
                try:
                    if not await channel_status_check(db_user.user_id):
                        await message.answer(
                            f'{translation.subscribe_channel.format(channel=f"@{TempData.SUB_CHANNEL}")}'
                        )
                        return False
                    logger.info(f"Пользователь подписан на канал {TempData.SUB_CHANNEL}")
                except Exception as e:
                    logger.critical(e)
    return True


async def is_validated(message, db_user, translation):
    if db_user.is_search:
        await message.answer(translation.wait_search)
        return False

    elif db_user.subscription.remaining_daily_limit == 0:  # todo 2/27/2022 5:39 PM taima: Вынести в бд
        await message.answer(
            # f"Закончился дневной лимит. Осталось запросов {db_user.subscription.remaining_daily_limit}.\n"
            # f"Купите подписку или ожидайте пополнения запросов в 00:00"
            translation.daily_limit_ended
        )
        return False

    # Проверка подписки на канал
    elif not await is_subscribe_to_channel(message, db_user, translation):
        return False

    return True
