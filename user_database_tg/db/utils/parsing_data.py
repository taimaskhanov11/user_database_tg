import argparse
import asyncio
import collections
import multiprocessing
import re
import time
from multiprocessing import current_process, Process
from pathlib import Path

from loguru import logger

from user_database_tg.config.config import TEST
from user_database_tg.db import models
from user_database_tg.db.db_main import init_tortoise, init_logging


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
            logger.debug(
                f"{current_process().name}|{self.service}|Буква {sign}| Создание объектов {len(data)}"
            )
            try:
                hacked_user = getattr(models, f"{sign}_HackedUser")
                logger.debug(hacked_user)
                objs = (
                    hacked_user(email=x[0], password=x[1], service=self.service)
                    for x in data
                )
                await hacked_user.bulk_create(
                    objs,
                    batch_size=self.batch_size,
                )
                logger.debug(
                    f"{current_process().name}|{self.service}|{sign}| Объекты созданы {len(data)}"
                )

            except Exception as e:
                logger.critical(e)
                self.write_errors(filename)

            self.users_data = collections.defaultdict(list)
            self.current_count = 0

    async def parce_datafiles(self):
        for data_file in self.path.iterdir():
            if data_file.name != "err_file.dd":
                sign = (
                    data_file.stem
                    if data_file.stem in ["dig_file", "sym_file"]
                    else data_file.name[0]
                )
                logger.trace(f"{current_process().name}| Парс файла {data_file.name}")
                for encode in ("utf-8", "cp1251"):
                    try:
                        if encode == "cp1251":
                            logger.warning(
                                f"{current_process().name}| Повторный парс файла c {encode} {self.service}|{data_file.name}"
                            )
                        with open(
                            data_file, encoding=encode
                        ) as f:  # todo 2/24/2022 12:40 AM taima:
                            t = time.monotonic()
                            for line in f:
                                self.all_count += 1
                                self.current_count += 1
                                self.users_data[sign].append(line)
                                if self.current_count >= self.batch_size:
                                    t2 = time.monotonic() - t
                                    logger.debug(
                                        f"{current_process().name}|{self.service}|{data_file.name}| Собрано данных {self.current_count}. {round(t2, 1)}s| Парс"
                                    )
                                    await self.create_users_obj(data_file.name)
                                    t = time.monotonic()

                            if self.users_data:
                                t2 = time.monotonic() - t
                                logger.debug(
                                    f"{current_process().name}|{self.service}|{data_file.name}| Парс оставшихся {len(self.users_data)}. {round(t2, 1)}s"
                                )
                                await self.create_users_obj(data_file.name)
                        break
                    except UnicodeDecodeError as e:
                        logger.critical(
                            f"{current_process().name}| {e}|not UTF8|{self.service}|{data_file.name}"
                        )
                        continue

            try:
                data_file.unlink()
                logger.info(f"Файл успешно {data_file.name} удален")
            except Exception as e:
                logger.warning(e)
                logger.warning(f"Ошибка при удалении файла {data_file.name}")


@logger.catch
async def create_users(path: Path):
    if TEST:
        await init_tortoise(host="localhost", password="postgres")
    else:
        await init_tortoise(host="localhost")

    service = path.name
    logger.debug(f"{current_process()}| Парс {service}...")
    t = time.monotonic()
    errors = ""
    data_parser = DataParser(path)
    try:
        await data_parser.parce_datafiles()

        logger.debug(f"Удаление паки {service} ")
        path.rmdir()
        logger.debug(f"Папка {service} успешно удалена")

    except Exception as e:
        logger.critical(e)
        # raise e
        errors += f"{current_process().name}|{service} Ошибка"
    t2 = time.monotonic() - t
    logger.info(
        f"{current_process().name}|{service}| Все данные сохранены {t2}s.Всего запарсено {data_parser.all_count} {errors}"
    )


@logger.catch
def run_async_create_users(path):
    logger.info(f"Запуск процесса {current_process().name}")
    asyncio.run(create_users(path))


@logger.catch
def run_process_create_users(main_path, processes=3):
    # logger.info(f"{current_process().name}| Всего юзеров {len(await HackedUser.all())}")
    # data_dir = Path("/var/lib/postgresql/TO_IMPORT")
    # data_dirs = list(data_dir.iterdir())
    if not main_path:
        logger.critical("Пустой путь")
        return
    data_dir = Path(main_path)
    if not data_dir.exists():
        logger.critical("Папка не найдена")
        return

    data_dirs = list(data_dir.iterdir())
    logger.info(f"Полученные папки {[d.name for d in data_dirs]}")
    logger.info("Запуск процессов...")
    time.sleep(5)
    prs = [Process(target=run_async_create_users, args=(path,)) for path in data_dirs]
    start_prs = []
    while True:
        if len(start_prs) >= processes:
            for start_pr in start_prs:
                if not start_pr.is_alive():
                    logger.warning(f"Завершение старого процесса {start_pr.name}")
                    start_prs.remove(start_pr)
                    try:
                        pr = prs.pop()
                        logger.success(
                            f"Создание процесса {pr.name}. Оставшиеся {prs}.Запущенные {start_prs}"
                        )
                        pr.start()
                        start_prs.append(pr)
                    except IndexError as e:
                        pass
        else:
            if not prs:
                if not start_prs:
                    logger.critical(
                        f"Завершение хендлера процессов {prs=}|{start_prs=}"
                    )
                    break
                else:
                    for start_pr in start_prs:
                        if not start_pr.is_alive():
                            logger.warning(
                                f"Завершение старого процесса {start_pr.name}"
                            )
                            start_prs.remove(start_pr)

                    logger.info(f"Ожидание завершения {start_prs=}")

            else:
                pr = prs.pop()
                logger.success(
                    f"Создание процесса {pr.name}. Оставшиеся {prs}.Запущенные {start_prs}"
                )
                pr.start()
                start_prs.append(pr)
        time.sleep(5)


def args_parce():
    pass


if __name__ == "__main__":
    init_logging()
    parser = argparse.ArgumentParser(description="Upload data in db")
    parser.add_argument("--path", type=str)
    args = parser.parse_args()
    print(args.path)
    run_process_create_users(args.path)
    pass
    # for data in users_data):
    #     print(data[0], data[1])
    # users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in data]
