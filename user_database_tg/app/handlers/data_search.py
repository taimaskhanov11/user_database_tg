import asyncio

from aiogram import Dispatcher, types
from loguru import logger

from user_database_tg.app.filters.email_filter import EmailFilter
from user_database_tg.app.utils.data_search_helpers import search_in_table, search_in_yandex, search_in_google
from user_database_tg.app.utils.validations import is_validated
from user_database_tg.db.models import DbUser, DbTranslation


async def part_sending(message, answer):
    if len(answer) > 4096:
        for x in range(0, len(answer), 4096):
            await message.answer(answer[x : x + 4096])
    else:
        await message.answer(answer)


@logger.catch
async def search_data(message: types.Message, db_user: DbUser, translation: DbTranslation):
    message.text = message.text.lower()
    if not db_user.language:
        db_user.language = "russian"
        await db_user.save()

    # Валидация
    if not await is_validated(message, db_user, translation):
        return

    async with db_user:
        # Поиск запроса в таблице
        table_result, yandex_result, google_result = await asyncio.gather(
            search_in_table(message, translation),
            search_in_yandex(message.text),
            search_in_google(message.text),
        )

        answer = f"{table_result}\n\n{yandex_result}\n\n{google_result}"

        # Отправка частями
        await part_sending(message, answer)

        # Отправка оставшегося лимита
        if db_user.subscription.remaining_daily_limit is not None:
            await message.answer(translation.left_attempts.format(limit=db_user.subscription.remaining_daily_limit))

        # Уменьшение дневного запроса на 1 при каждом запросе
        await db_user.subscription.decr()


async def incorrect_email(message: types.Message):
    logger.debug(f"Некорректный email. {message.text}")
    await message.answer("Некорректный email")


def register_data_search_handlers(dp: Dispatcher):
    # dp.register_message_handler(search_data, lambda m: m.text[0].isalpha() and "@" in m.text)
    dp.register_message_handler(search_data, EmailFilter())
    dp.register_message_handler(incorrect_email)
