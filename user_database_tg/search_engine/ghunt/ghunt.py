import asyncio
import os
import sys
import time
from pathlib import Path

from loguru import logger

from user_database_tg.search_engine.ghunt.modules.doc import doc_hunt
from user_database_tg.search_engine.ghunt.modules.email import email_hunt
from user_database_tg.search_engine.ghunt.modules.gaia import gaia_hunt
from user_database_tg.search_engine.ghunt.modules.youtube import youtube_hunt


def time_track(func):
    async def wrapper(*args, **kwargs):
        now = time.monotonic()
        res = await func(*args, **kwargs)
        logger.warning(f"Executing time {time.monotonic() - now}")
        return res

    return wrapper


def pretty_view(data) -> str:
    answer = ""
    answer += f"{len(data['accounts'])} account found\n"
    for acc in data["accounts"]:
        for key, value in acc.items():
            answer += f"{key}: {value}\n"
        answer += "\n"
    return answer


# @time_track
async def get_google_account_info(email) -> str:
    try:
        return pretty_view(await email_hunt(email))
    except Exception as e:
        logger.warning(e)
        # todo 25.03.2022 19:18 taima: вернуть пустой
        return str(e)


if __name__ == "__main__":
    logger.remove()
    logger.add(
        sink=sys.stderr,
        level="TRACE",
        enqueue=True,
        diagnose=True,
    )

    # 3.7 - 5.4 ~ 4.5
    # print(asyncio.run(get_google_account_info("charlskenno@gmail.com")))
    logger.success(asyncio.run(get_google_account_info("larry@google.com")))
    exit()
    # ~ 2.3
    # We change the current working directory to allow using GHunt from anywhere
    os.chdir(Path(__file__).parents[0])

    modules = ["email", "doc", "gaia", "youtube"]

    if len(sys.argv) <= 1 or sys.argv[1].lower() not in modules:
        print("Please choose a module.\n")
        print("Available modules :")
        for module in modules:
            print(f"- {module}")
        exit()

    module = sys.argv[1].lower()
    if len(sys.argv) >= 3:
        data = sys.argv[2]
    else:
        data = None

    if module == "email":
        email_hunt(data)
    elif module == "doc":
        doc_hunt(data)
    elif module == "gaia":
        gaia_hunt(data)
    elif module == "youtube":
        youtube_hunt(data)
