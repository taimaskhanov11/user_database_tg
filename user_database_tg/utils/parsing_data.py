import collections
import re
import time
from multiprocessing import current_process
from pathlib import Path
from pprint import pprint

from loguru import logger

from user_database_tg.db.models import HackedUser


def parce_datafile_dict(path: str) -> list[dict]:
    """Парсинг данных пользователя и файлов"""

    users_data = []
    for data_dir in Path(path).iterdir():
        for data_file in data_dir.iterdir():
            with open(data_file, encoding="utf-8") as f:
                # print(f.readlines())
                data = map(
                    lambda x: {
                        "email": x[0],
                        "password": x[1],
                        "service": data_dir.name
                    },
                    map(
                        lambda x: re.findall(r"(.*):(.*)", x.strip())[0], f.readlines()
                    )
                )

                # users_da
                users_data.extend(list(data))
                # pprint(list(data))
            # break
        # break
    return users_data


def parce_datafile_alphabet(path: str) -> dict[str, tuple[str, str]]:
    """Парсинг данных пользователя и файлов по алфавиту"""

    users_data = {}
    for data_dir in Path(path).iterdir():
        for data_file in data_dir.iterdir():
            with open(data_file, encoding="utf-8") as f:
                # print(f.readlines())
                data = tuple(map(lambda x: re.findall(r"(.*):(.*)", x.strip())[0], f.readlines()))
                users_data[data_file.name[0]] = tuple(data)
                # users_data.extend(list(data))
                # print(users_data)
            # break
        # break
    return users_data


def parce_datafiles_dict(path: str) -> dict[tuple[str, str]]:
    users_data = collections.defaultdict(list)
    for data_dir in Path(path).iterdir():
        for data_file in data_dir.iterdir():
            if data_file.name != "err_file.dd":
                print(data_file.name)
                with open(data_file, encoding="utf-8") as f:
                    # print(f.readlines())
                    try:
                        data = tuple(map(lambda x: re.findall(r"(.*):(.*)", x.strip())[0], f.readlines()))
                        # users_da
                        users_data[data_dir.name].extend(list(data))
                    except Exception as e:
                        logger.exception(data_file.name)
                        raise e
                # users_data.extend(list(data))
                # print(users_data)
            # break
        # break
    return users_data


@logger.catch
async def parce_datafiles(path: Path, batch_size):
    users_data = []
    service = path.name
    parce_count = 0

    def parce_user(data):
        login, password = re.findall(r"(.*):(.*)", data)[0]
        if login > 254:
            login = login[:254]
        if password > 254:
            password = password[:254]
        return login.replace("\x00", " "), password.replace("\x00", " ")

    @logger.catch
    async def bulk_users_create(objs):
        try:
            await HackedUser.bulk_create(
                objs,
                batch_size=batch_size,
            )
        except Exception as e:
            logger.critical(e)
            with open("trash.txt", "a", encoding="utf-8") as f:
                logger.debug("Запись в файл")
                f.write(f"{path.name}{data_file.name}\n")
                # f.writelines(map(lambda x: f"{x[0]}:{x[1]}\n", users_data[pre:index]))
            # raise e

    async def parce_data():
        data = list(map(parce_user, users_data))
        logger.debug(f"{current_process().name}|{service}|{data_file.name}| Создание объектов {len(data)}")
        users_objs = (HackedUser(email=x[0], password=x[1], service=service) for x in data)
        await bulk_users_create(users_objs)
        logger.debug(f"{current_process().name}|{service}|{data_file.name}| Объекты созданы {len(data)}")

    for data_file in path.iterdir():
        if data_file.name != "err_file.dd":
            logger.trace(f"{current_process().name}| Парс файла {data_file.name}")
            try:
                with open(data_file, encoding="utf-8") as f:  # todo 2/24/2022 12:40 AM taima:
                    t = time.monotonic()
                    for line in f:
                        parce_count += 1
                        users_data.append(line)
                        if len(users_data) >= batch_size:
                            t2 = time.monotonic() - t
                            logger.debug(
                                f"{current_process().name}|{service}|{data_file.name}| Запарсено данных {len(users_data)}. {round(t2, 1)}s")
                            await parce_data()
                            users_data = []
                            t = time.monotonic()
                    if users_data:
                        t2 = time.monotonic() - t
                        logger.debug(
                            f"{current_process().name}|{service}|{data_file.name}| Парс оставшихся {len(users_data)}. {round(t2, 1)}s")
                        await parce_data()
                        users_data = []
                        t = time.monotonic()


            except UnicodeDecodeError as e:
                logger.critical(f"{current_process().name}| {e}| UTF8|{path.name}|{data_file.name}")
                logger.warning(f"{current_process().name}| Повторный парс файла {path.name}|{data_file.name}")
                with open(data_file, encoding="cp1251") as f:  # todo 2/24/2022 12:40 AM taima:
                    t = time.monotonic()
                    for line in f:
                        users_data.append(line)
                        if len(users_data) == batch_size:
                            t2 = time.monotonic() - t
                            logger.debug(
                                f"{current_process().name}|{service}|{data_file.name}| Запарсено данных {len(users_data)}. {t2} s")
                            await parce_data()
                            users_data = []
                            t = time.monotonic()
                    if users_data:
                        t2 = time.monotonic() - t
                        logger.debug(
                            f"{current_process().name}|{service}|{data_file.name}| Запарсено данных {len(users_data)}. {round(t2, 1)}s")
                        await parce_data()
                        users_data = []
                        t = time.monotonic()
    return parce_count


if __name__ == '__main__':
    users_data = parce_datafiles(Path("../temp/users_datafiles/000webhost.com_(2015.03)"))
    pprint(users_data)
    # for data in users_data):
    #     print(data[0], data[1])
    # users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in data]
