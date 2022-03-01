from aiogram import Dispatcher, types
from loguru import logger

from user_database_tg.app.filters.email_filter import EmailFilter
from user_database_tg.app.translation.message_translation import Translation
from user_database_tg.db.models import *

NO_FIND_EMAIL = []


async def search_data(
        message: types.Message, db_user: DbUser, translation: DbTranslation
):
    # logger.critical(db_user)
    # logger.info("6.Handler")
    # logger.debug(middleware_data)
    # logger.debug(from_filter)

    if db_user.is_search:
        await message.answer(translation.wait_search)
        return

    if (
            db_user.subscription.remaining_daily_limit == 0
    ):  # todo 2/27/2022 5:39 PM taima: Вынести в бд
        await message.answer(
            # f"Закончился дневной лимит. Осталось запросов {db_user.subscription.remaining_daily_limit}.\n"
            # f"Купите подписку или ожидайте пополнения запросов в 00:00"
            translation.daily_limit_ended.format(
                limit=db_user.subscription.remaining_daily_limit
            )
        )
        return

    try:
        # Проверка буквы запроса для поиска в определенной таблице
        sign = message.text[0]
        if sign.isalpha():
            hack_model = globals()[f"{sign}_HackedUser"]
        elif sign.isdigit():
            hack_model = globals()[f"dig_file_HackedUser"]
        else:
            hack_model = globals()[f"sym_file_HackedUser"]
    except Exception as e:
        logger.critical(e)
        return

    # Уменьшение дневного запроса на 1 при каждом запросе
    if db_user.subscription.daily_limit is not None:
        db_user.subscription.remaining_daily_limit -= 1
        await db_user.subscription.save()

    # Включение режима блокировки пока запрос не завершиться
    db_user.is_search = True
    await db_user.save()

    # Поиск запроса в таблице
    logger.debug(f"Поиск {message.text} в таблице {hack_model.__name__}")
    if message.text in NO_FIND_EMAIL:
        logger.info("Найден в в переменой")
        answer = translation.data_not_found.format(email=message.text)
        if db_user.subscription.remaining_daily_limit is not None:
            answer += "\n" + translation.left_attempts.format(limit=db_user.subscription.remaining_daily_limit)
    else:
        res = await hack_model.filter(email=message.text)
        if not res:
            NO_FIND_EMAIL.append(message.text)
            answer = translation.data_not_found.format(email=message.text)
        else:
            answer = "\n\n".join([f"{h.service}\n{h.email}|password: {h.password}|" for h in res])
        # answer += f"\nОсталось попыток {db_user.subscription.remaining_daily_limit}"
        if db_user.subscription.remaining_daily_limit is not None:
            answer += "\n" + translation.left_attempts.format(limit=db_user.subscription.remaining_daily_limit)
    # Ответ и отключение режима поиска

    if len(answer) > 4096:
        for x in range(0, len(answer), 4096):
            await message.answer(answer[x:x + 4096])
    else:
        await message.answer(answer)

    # await message.answer(answer)
    db_user.is_search = False
    await db_user.save()


def register_data_search_handlers(dp: Dispatcher):
    # dp.register_message_handler(search_data, lambda m: m.text[0].isalpha() and "@" in m.text)
    dp.register_message_handler(search_data, EmailFilter())
