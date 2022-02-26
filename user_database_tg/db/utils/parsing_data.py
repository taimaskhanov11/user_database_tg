import collections
import re
import time
from multiprocessing import current_process
from pathlib import Path

from loguru import logger

from user_database_tg.db import models


class DataParser:
    """DataParser"""

    def __init__(self, path: Path, batch_size: int = 500000):

        self.users_data = collections.defaultdict(list)
        self.path = path
        self.all_count = 0
        self.current_count = 0
        self.service = path.name
        self.batch_size = batch_size

    @staticmethod
    def validate_data(user_data):
        login, password = re.findall(r"(.*):(.*)", user_data)[0]
        if len(login) > 254:
            login = login[:254]
        if len(password) > 254:
            password = password[:254]
        return login.replace("\x00", " "), password.replace("\x00", " ")

    def write_errors(self, filename):
        with open("error_files.txt", "a", encoding="utf-8") as f:
            logger.debug("Запись в файл")
            f.write(f"{self.service}|{filename}\n")

    async def create_users_obj(self, filename):
        # pprint(self.users_data)
        for sign, data in self.users_data.items():
            # logger.critical(f"{sign}|{data}")
            data = list(map(self.validate_data, data))
            logger.debug(f"{current_process().name}|{self.service}|Буква {sign}| Создание объектов {len(data)}")
            try:
                hacked_user = getattr(models, f"{sign}_HackedUser")
                logger.debug(hacked_user)
                objs = (hacked_user(email=x[0], password=x[1], service=self.service) for x in data)
                await hacked_user.bulk_create(
                    objs,
                    batch_size=self.batch_size,
                )
                logger.debug(f"{current_process().name}|{self.service}|{sign}| Объекты созданы {len(data)}")

            except Exception as e:
                logger.critical(e)
                self.write_errors(filename)

            self.users_data = collections.defaultdict(list)
            self.current_count = 0

    async def parce_datafiles(self):
        for data_file in self.path.iterdir():
            if data_file.name != "err_file.dd":
                sign = data_file.stem if data_file.stem in ["dig_file", "sym_file.dd"] else data_file.name[0]
                logger.trace(f"{current_process().name}| Парс файла {data_file.name}")
                for encode in ("utf-8", "cp1251"):
                    try:
                        if encode == "cp1251":
                            logger.warning(
                                f"{current_process().name}| Повторный парс файла c {encode} {self.service}|{data_file.name}")
                        with open(data_file, encoding=encode) as f:  # todo 2/24/2022 12:40 AM taima:
                            t = time.monotonic()
                            for line in f:
                                self.all_count += 1
                                self.current_count += 1
                                self.users_data[sign].append(line)
                                if self.current_count >= self.batch_size:
                                    t2 = time.monotonic() - t
                                    logger.debug(
                                        f"{current_process().name}|{self.service}|{data_file.name}| Собрано данных {self.current_count}. {round(t2, 1)}s| Парс")
                                    await self.create_users_obj(data_file.name)
                                    t = time.monotonic()

                            if self.users_data:
                                t2 = time.monotonic() - t
                                logger.debug(
                                    f"{current_process().name}|{self.service}|{data_file.name}| Парс оставшихся {len(self.users_data)}. {round(t2, 1)}s")
                                await self.create_users_obj(data_file.name)
                        break
                    except UnicodeDecodeError as e:
                        logger.critical(f"{current_process().name}| {e}|not UTF8|{self.service}|{data_file.name}")
                        continue


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
    pass
    # for data in users_data):
    #     print(data[0], data[1])
    # users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in data]
