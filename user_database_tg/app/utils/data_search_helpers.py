import collections
import re
from pprint import pprint
from typing import Optional

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

    return answer
    # return f"[SEARCH EMAILS]\n{answer}"


# todo 26.03.2022 12:17 taima: вынести в бд
russian_dict = {
    "image": "фото",
    "gender": "пол",
    "name": "имя",
    "fullname": "полное имя",
    "Get info by": "Информация по",
    "account found": "Найденных аккаунтов",
    "username": "Имя пользователя",
    "Last profile edit": "Последнее редактирование профиля",
    "Profile picture": "Фото профиля",
    "email": "Почта",
    "Name": "Имя",
}


def google_pretty_view(data: Optional[dict], language) -> str:
    if not data:
        return "Мейл не найден в базе google."
    answer = ""
    if language == "russian":
        answer += f"{len(data['accounts'])} {russian_dict.get('account found')}\n"
    else:
        answer += f"{len(data['accounts'])} account found\n"
    for acc in data["accounts"]:
        for key, value in acc.items():
            if key in ["Google Maps", "Google Calendar"]:
                continue

            if "YouTube channel" in key:
                percent = re.findall(r"=> (\d+).\d+%", key)
                if percent:
                    if int(percent[0]) < 50:
                        continue

            if "Probable location" in key:
                if "low" in key.lower():
                    continue

            if language == "russian":
                if "YouTube channel" in key:
                    key = f"Ютуб-канал (достоверность информации {percent[0]}%)"
                elif "Probable location" in key:
                    percent2 = re.findall(r"=> (\w.+)\)", key)
                    key = f"Возможное местоположение (достоверность {percent2})"

                if key in russian_dict:
                    key = russian_dict.get(key)

            answer += f"{key}: {value}\n"
        answer += "\n"
    return answer


def yandex_pretty_view(data: Optional[dict], language):
    if not data:
        return "Мейл не найден в базе yandex."

    answer = ""
    for by, sites_results in data.items():

        if "[*] Get info by yandex_messenger_guid" in by:
            continue

        if language == "russian":
            by: str = by.replace("Get info by", russian_dict["Get info by"])

        if "yandex_public_id" in by:
            pass
        else:
            answer += f"\n{by}\n"

        for sitename, data in sites_results.items():
            if not data:
                # answer += "\n\tNot found.\n"
                continue
            answer += f"\n[+] Yandex.{sitename.capitalize()}"

            if "URL" in data:
                answer += f'\n\tURL: {data.get("URL")}'
            for k, v in data.items():
                # if k in [
                #     "cards",
                #     "boards",
                #     "is_passport",
                #     "is_restricted",
                #     "is_forbid",
                #     "is_km",
                #     "is_business",
                #     "is_org",
                #     "is_banned",
                #     "is_deleted",
                #     "is_hidden_name",
                #     "is_verified",
                # ]:
                #     continue
                if k not in [
                    "yandex_public_id",
                    # "yandex_uid",
                    "id",
                    "username",
                    "fullname",
                    "URL",
                    # "email",
                    "image",
                ]:
                    continue

                if v in answer:
                    continue

                logger.trace(f"{k}, {v}")
                if k != "URL":
                    # if by in "[*] Get info by username":
                    #     for pub in sites_results:
                    #         if "[*] Get info by yandex_public_id" in pub:
                    #             yandex_public_id = re.findall("[*] Get info by yandex_public_id `(.+)`", pub)
                    #             answer += f"\n\tyandex_public_id: {yandex_public_id[0]}"

                    if language == "russian":
                        if k in russian_dict:
                            k = russian_dict.get(k)

                    answer += f"\n\t{k.capitalize()}: {v}"
            answer += "\n"
    return answer


# todo 26.03.2022 14:10 taima: поправить
async def search_in_yandex(email: str, language: str) -> str:
    if email.split("@")[1] == "yandex.ru":
        result = await get_yandex_account_info(email)
        logger.trace(result)
        view = yandex_pretty_view(result, language)
        return view
        # return f"[SEARCH IN YANDEX ENGINE]\n{view}"
    return ""


async def search_in_google(email: str, language: str) -> str:
    if email.split("@")[1] == "gmail.com":
        result = await get_google_account_info(email)
        logger.trace(result)
        view = google_pretty_view(result, language)
        return view
        # return f"[SEARCH IN GOOGLE ENGINE]\n{view}"
    return ""
