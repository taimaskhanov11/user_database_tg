import asyncio

from loguru import logger

from user_database_tg.app.translation.google_translation import translate
from user_database_tg.db.models import DbTranslation


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
