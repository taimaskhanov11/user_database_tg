import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from user_database_tg.app import markups
from user_database_tg.app.filters.email_filter import EmailFilter
from user_database_tg.app.utils.data_search_helpers import search_in_table, search_in_yandex, search_in_google
from user_database_tg.app.utils.validations import is_validated
from user_database_tg.db.models import DbUser, DbTranslation


async def part_sending(message, answer, add_info: bool):
    # answer += "*" * 40000
    # answer += "312312312312312"
    logger.trace(add_info)
    logger.trace(f"Message sign count {len(answer)}")
    limit = 50000

    if len(answer) > 4096:

        if len(answer) > limit:
            for i in range(50):
                if answer[limit] == "\n":
                    break
                limit += 1
            answer = answer[:limit]

        for x in range(0, len(answer), 4096):
            y = x + 4096
            if y >= len(answer) and add_info:
                logger.trace("Add info")
                await message.answer(answer[x: y], reply_markup=markups.add_info)
            else:
                await message.answer(answer[x: y])
            await asyncio.sleep(0.2)
    else:
        await message.answer(answer, reply_markup=markups.add_info if add_info else None)


# @logger.catch
async def search_data(message: types.Message, db_user: DbUser, translation: DbTranslation, state: FSMContext):
    message.text = message.text.lower()
    if not db_user.language:
        db_user.language = "russian"
        await db_user.save()

    # Валидация
    if not await is_validated(message, db_user, translation):
        return

    async with db_user:
        # Поиск запроса в таблице
        await message.answer("Идет поиск, ожидайте...")
        table_result, yandex_result, google_result = await asyncio.gather(
            search_in_table(message, translation),
            search_in_yandex(message.text, translation.language),
            search_in_google(message.text, translation.language),
            # return_exceptions=True
        )

        # answer = f"{table_result}\n\n"

        await state.update_data(add_info=f"{yandex_result or google_result}")

        # Отправка частями
        await part_sending(message, table_result, bool(yandex_result or google_result))
        # if yandex_result or google_result:
        #     await message.answer("Узнать дополнительную информацию по почте", reply_markup=markups.add_info)

        # Уменьшение дневного запроса на 1 при каждом запросе
        await db_user.subscription.decr()

        # Отправка оставшегося лимита
        if db_user.subscription.remaining_daily_limit is not None:
            await message.answer(translation.left_attempts.format(limit=db_user.subscription.remaining_daily_limit))


async def get_add_info(call: types.CallbackQuery, state: FSMContext):
    info = await state.get_data()
    await call.message.answer(info["add_info"] or "Не найдено")
    await state.finish()


async def incorrect_email(message: types.Message):
    logger.debug(f"Некорректный email. {message.text}")
    await message.answer("Некорректный email")


def register_data_search_handlers(dp: Dispatcher):
    # dp.register_message_handler(search_data, lambda m: m.text[0].isalpha() and "@" in m.text)
    dp.register_message_handler(search_data, EmailFilter())
    dp.register_message_handler(incorrect_email)
    dp.register_callback_query_handler(get_add_info, text="add_info")
