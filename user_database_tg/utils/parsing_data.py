import collections
import re
from pathlib import Path
from pprint import pprint


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


def parce_datafile(path: str) -> dict[tuple[str, str]]:
    users_data = collections.defaultdict(list)
    for data_dir in Path(path).iterdir():
        for data_file in data_dir.iterdir():
            with open(data_file, encoding="utf-8") as f:
                # print(f.readlines())
                data = tuple(map(lambda x: re.findall(r"(.*):(.*)", x.strip())[0], f.readlines()))
                # users_da
                users_data[data_dir.name].extend(list(data))
                # users_data.extend(list(data))
                # print(users_data)
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


if __name__ == '__main__':
    pprint(parce_datafile("../users_datafiles"))
