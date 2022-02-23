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
    for data_file in path.iterdir():
        if data_file.name != "err_file.dd":
            logger.trace(f"Парс файла {data_file.name}")
            with open(data_file, encoding="utf-8") as f:
                # print(f.readlines())
                try:
                    data = tuple(map(lambda x: re.findall(r"(.*):(.*)", x.strip())[0], f.readlines()))
                    # users_da
                    users_data.extend(list(data))
                except Exception as e:
                    logger.exception(data_file.name)
                    raise e
    return users_data


if __name__ == '__main__':
    pprint(parce_datafiles("../users_datafiles"))
