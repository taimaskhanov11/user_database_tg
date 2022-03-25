import collections

from aiogram import types
from loguru import logger

from user_database_tg.config.config import TempData
from user_database_tg.db.models import *
from user_database_tg.search_engine.ghunt.ghunt import get_google_account_info
from user_database_tg.search_engine.yaseeker.ya_seeker import get_yandex_account_info


async def search_in_table(message: types.Message, translation: DbTranslation) -> str:
    # Проверка буквы запроса для поиска в определенной таблице

    sign = message.text[0]
    if sign.isalpha():
        hack_model = globals()[f"{sign}_HackedUser"]
    elif sign.isdigit():
        hack_model = globals()[f"dig_file_HackedUser"]
    else:
        hack_model = globals()[f"sym_file_HackedUser"]

    logger.debug(f"Поиск {message.text} в таблице {hack_model.__name__}")
    find_count = 0

    if message.text in TempData.NO_FIND_EMAIL:
        logger.info("Найден в в переменой")
        answer = translation.data_not_found.format(email=message.text)
    else:
        db_res = await hack_model.filter(email=message.text)
        Limit.number_day_requests += 1
        if not db_res:
            TempData.NO_FIND_EMAIL.append(message.text)
            answer = translation.data_not_found.format(email=message.text)
        else:
            answer = "______________________________\n"
            find_dict = collections.defaultdict(set)
            for h in db_res:
                find_dict[h.service].add(f"{h.email}: {h.password}")

            for s, hstr in find_dict.items():
                find_count += len(hstr)
                answer = answer + s + "\n" + "\n".join(hstr)
                answer += "\n\n"

    if find_count:
        answer += f"\nНайдено всего {find_count}"

    return f"[SEARCH EMAILS]\n{answer}"


async def search_in_yandex(email) -> str:
    if email.split("@")[1] == "yandex.ru":
        result = await get_yandex_account_info(email)
        return f"[SEARCH IN YANDEX ENGINE]\n{result}"
    return ""


async def search_in_google(email) -> str:
    if email.split("@")[1] == "gmail.com":
        result = await get_google_account_info(email)
        return f"[SEARCH IN GOOGLE ENGINE]\n{result}"
    return ""
