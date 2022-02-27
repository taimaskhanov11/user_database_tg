import re
from pathlib import Path


def open_big_file(path, encoding="utf-8"):
    path = path or Path("/var/lib/postgresql/TO_IMPORT/unknown_site_name")
    with open(path, encoding=encoding) as f:
        for i in range(50):
            print(f.readline())


if __name__ == "__main__":
    pass
    # find_email("aahaantourandtravels01@gmail.com:Yog@1987")
