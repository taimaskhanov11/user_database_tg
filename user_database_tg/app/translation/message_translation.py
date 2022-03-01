import asyncio
from pprint import pprint
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from user_database_tg.app.translation.google_translation import translate
from user_database_tg.db.db_main import init_db
from user_database_tg.db.models import DbTranslation


class Translation(BaseModel):
    db_message: Optional[DbTranslation]

    # start
    start_message: str

    # menu
    profile: str
    description: str
    support: str
    subscribe: str

    # menu buttons
    profile_b: str
    description_b: str
    support_b: str
    subscribe_b: str

    # waiting for end search
    wait_search: str
    data_not_found: str

    # waiting for pay
    create_payment: str
    wait_payment: str
    go_payment_b: str

    reject_payment: str
    reject_payment_b: str

    class Config:
        arbitrary_types_allowed = True


async def init_translations2():
    # await init_db()
    for db_message in await DbTranslation.all():
        logger.trace(repr(dict(db_message)))
        translation = Translation(**dict(db_message), db_message=db_message)
        TRANSLATIONS[db_message.language] = translation
    logger.debug("Перевод на английский вариант")
    rus: Translation = TRANSLATIONS["russian"]
    tasks = []
    for key, value in rus.dict().items():
        if key == "db_message":
            continue
        tasks.append(asyncio.create_task(translate(key, value)))
    res = await asyncio.gather(*tasks)
    en_fields_data = {}
    for d in res:
        en_fields_data.update(d)
    en_translation = Translation(**dict(en_fields_data))
    TRANSLATIONS["english"] = en_translation
    logger.debug("Перевод Инициализирован")


async def init_english():
    logger.debug("Перевод на английский вариант")
    rus: DbTranslation = TRANSLATIONS["russian"]
    tasks = []
    # pprint(dict(rus))
    for key, value in dict(rus).items():
        # logger.critical(f"{key}{value}")
        if key == "id":
            continue
        tasks.append(asyncio.create_task(translate(key, value)))
    res = await asyncio.gather(*tasks)
    en_fields_data = {}
    for d in res:
        en_fields_data.update(d)

    en_fields_data["language"] = "english"
    en_fields_data["title"] = "English language"
    en_translation = await DbTranslation.create(**dict(en_fields_data))
    TRANSLATIONS["english"] = en_translation
    logger.debug("Английский переведен из загружен")


async def init_translations():
    for trans in await DbTranslation.all():
        TRANSLATIONS[trans.language] = trans

    if "english" not in TRANSLATIONS:
        await init_english()
    logger.debug("Переводы Инициализированы")


TRANSLATIONS: [str, DbTranslation] = {}


async def go_translate():
    # translator = Translator()
    # print(translator.translate("Hello World"))
    tasks = []


if __name__ == "__main__":
    asyncio.run(init_translations())
    # asyncio.run(go_translate())
    # go_translate()
    # print(translations)
