import collections
import re
from pathlib import Path
from pprint import pprint

from loguru import logger


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


def parce_datafiles(path: Path) -> list[tuple[str, str]]:
    users_data = []

    def parce_user(data):
        # data = data.strip() #todo 2/24/2022 6:38 PM taima:
        # if data == "\n":
        #     print(data)
        # return re.findall(r"(.*):(.*)", data)[0] or "null", "null"
        # logger.trace(data)
        # if data:
        #     login, password = re.findall(r"(.*):(.*)", data)[0]
        #     return login.replace("\x00", " "), password.replace("\x00", " ")
        # else:
        #     logger.critical(data)
        #     return "null", "null"
        # if data:
        login, password = re.findall(r"(.*):(.*)", data)[0]
        return login.replace("\x00", " "), password.replace("\x00", " ")
        # else:
        #     logger.critical(data)
        #     return "null", "null"

    def parce_data(f):
        # print(f.readlines())
        data = list(
            # map(lambda x: re.findall(r"(.*):(.*)", x.strip())[0] if x.strip() and "0x00" not in x else (
            # map(lambda x: re.findall(r"(.*):(.*)", x.strip())[0] if x.strip() else ("null", "null"), f.readlines()))
            map(parce_user, f.readlines()))  # todo 2/24/2022 2:00 AM taima: filter
        # map(lambda x: re.findall(r"(.*):(.*)", x)[0], f.readlines()))  # todo 2/24/2022 2:00 AM taima: filter
        # map(lambda x: re.findall(r"(.*):(.*)", x.decode("utf-8"))[0], f.readlines()))  # todo 2/24/2022 2:00 AM taima: filter
        # users_da
        logger.debug(f"Получено {data_file.name}|[{len(data)}]")
        users_data.extend(data)

    for data_file in path.iterdir():
        # for data_file in [Path(r"C:\Users\taima\PycharmProjects\user_database_tg\user_database_tg\db\trash.txt")]:
        if data_file.name != "err_file.dd":
            logger.trace(f"Парс файла {data_file.name}")
            try:
                with open(data_file, encoding="utf-8") as f:  # todo 2/24/2022 12:40 AM taima:
                    # with open(data_file, mode="rb") as f:  # todo 2/24/2022 12:40 AM taima:
                    # print(f.readlines())
                    # print(f)
                    parce_data(f)
                    # continue
            except UnicodeDecodeError as e:
                logger.critical(f"{e}| UTF8|{path.name}|{data_file.name}")
                # continue  # todo 2/24/2022 3:46 PM taima:
                logger.warning(f"Повторный парс файла {path.name}|{data_file.name}")
                with open(data_file, encoding="cp1251") as f:  # todo 2/24/2022 12:40 AM taima:
                    # print(f.readlines())
                    parce_data(f)

    return users_data


if __name__ == '__main__':
    users_data = parce_datafiles(Path("../users_datafiles/000webhost.com_(2015.03)"))
    pprint(users_data)
    # for data in users_data):
    #     print(data[0], data[1])
    # users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in data]
