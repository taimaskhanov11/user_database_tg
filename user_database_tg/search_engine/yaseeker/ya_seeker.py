import asyncio
import collections
import json
import os
from http.cookiejar import MozillaCookieJar
from pprint import pprint

from aiohttp import ClientSession
from loguru import logger
from socid_extractor import extract

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
}

COOKIES_FILENAME = "ya_cookies/cookies.txt"


def load_cookies(filename):
    cookies = {}
    if os.path.exists(filename):
        cookies_obj = MozillaCookieJar(filename)
        cookies_obj.load(ignore_discard=False, ignore_expires=False)

        for domain in cookies_obj._cookies.values():
            for cookie_dict in list(domain.values()):
                for _, cookie in cookie_dict.items():
                    cookies[cookie.name] = cookie.value

    return cookies


cookies = load_cookies(COOKIES_FILENAME)


class IdTypeInfoAggregator:
    acceptable_fields = ()

    def __init__(self, identifier: str, cookies: dict):
        self.identifier = identifier
        self.cookies = cookies
        self.info = {}
        self.sites_results = {}

    @classmethod
    def validate_id(cls, name, identifier):
        return name in cls.acceptable_fields

    def aggregate(self, info: dict):
        for k, v in info.items():
            if k in self.info:
                if isinstance(self.info[k], set):
                    self.info[k].add(v)
                else:
                    self.info[k] = {self.info[k], v}
            else:
                self.info[k] = v

    async def simple_get_info_request(
        self, url: str, headers_updates: dict = None, orig_url: str = None, session: ClientSession = None
    ) -> dict:
        headers = dict(HEADERS)
        headers.update(headers_updates if headers_updates else {})
        async with session.get(url, headers=headers, cookies=self.cookies) as response:
            # r = requests.get(url, headers=headers, cookies=self.cookies)
            text = await response.text()
            if "enter_captcha_value" in text:
                info = {"Error": "Captcha detected"}
            else:
                try:
                    info = extract(text)
                except Exception as e:
                    print(f"Error for URL {url}: {e}\n")
                    info = {}
                if info:
                    info["URL"] = orig_url or url
        return info

    async def collect(self):
        get_methods: list = []
        method_names: list = []
        for f in self.__dir__():
            if f.startswith("get_"):
                name = " ".join(f.split("_")[1:-1])
                get_methods.append(getattr(self, f))
                method_names.append(name)
        async with ClientSession() as session:
            info_result = await asyncio.gather(*[method(session=session) for method in get_methods])
            # logger.info(info_result)

            for name, info in zip(method_names, info_result):
                logger.trace(f"{name}{info}")
                self.sites_results[name] = info
                self.aggregate(info)

    def print(self):
        for sitename, data in self.sites_results.items():
            print("[+] Yandex." + sitename.capitalize())
            if not data:
                print("\tNot found.\n")
                continue

            if "URL" in data:
                print(f'\tURL: {data.get("URL")}')
            for k, v in data.items():
                if k != "URL":
                    print("\t" + k.capitalize() + ": " + v)
            print()


class YaUsername(IdTypeInfoAggregator):
    acceptable_fields = ("username",)

    async def get_collections_API_info(self, session=None) -> dict:
        return await self.simple_get_info_request(
            url=f"https://yandex.ru/collections/api/users/{self.identifier}",
            orig_url=f"https://yandex.ru/collections/user/{self.identifier}/",
            session=session,
        )

    async def get_music_info(self, session=None) -> dict:
        orig_url = f"https://music.yandex.ru/users/{self.identifier}/playlists"
        referer = {"referer": orig_url}
        return await self.simple_get_info_request(
            url=f"https://music.yandex.ru/handlers/library.jsx?owner={self.identifier}",
            orig_url=orig_url,
            headers_updates=referer,
            session=session,
        )

    async def get_bugbounty_info(self, session=None) -> dict:
        return await self.simple_get_info_request(
            f"https://yandex.ru/bugbounty/researchers/{self.identifier}/", session=session
        )

    async def get_messenger_search_info(self, session: ClientSession = None) -> dict:
        url = "https://yandex.ru/messenger/api/registry/api/"
        data = {
            "method": "search",
            "params": {"query": self.identifier, "limit": 10, "entities": ["messages", "users_and_chats"]},
        }

        async with session.post(
            url, headers=HEADERS, cookies=self.cookies, data={"request": (None, json.dumps(data))}
        ) as response:
            text = await response.text()
            # r = requests.post(url, headers=HEADERS, cookies=self.cookies, files={'request': (None, json.dumps(data))})
            info = extract(text)
            if info and info.get("yandex_messenger_guid"):
                info["URL"] = f'https://yandex.ru/chat#/user/{info["yandex_messenger_guid"]}'
        return info

    async def get_music_API_info(self, session=None) -> dict:
        return await self.simple_get_info_request(
            f"https://api.music.yandex.net/users/{self.identifier}", session=session
        )


class YaPublicUserId(IdTypeInfoAggregator):
    acceptable_fields = (
        "yandex_public_id",
        "id",
    )

    @classmethod
    def validate_id(cls, name, identifier):
        return len(identifier) == 26 and name in cls.acceptable_fields

    async def get_collections_API_info(self, session=None) -> dict:
        return await self.simple_get_info_request(
            url=f"https://yandex.ru/collections/api/users/{self.identifier}",
            orig_url=f"https://yandex.ru/collections/user/{self.identifier}/",
            session=session,
        )

    async def get_reviews_info(self, session=None) -> dict:
        return await self.simple_get_info_request(f"https://reviews.yandex.ru/user/{self.identifier}", session=session)

    async def get_znatoki_info(self, session=None) -> dict:
        return await self.simple_get_info_request(f"https://yandex.ru/q/profile/{self.identifier}/", session=session)

    async def get_zen_info(self, session=None) -> dict:
        return await self.simple_get_info_request(f"https://zen.yandex.ru/user/{self.identifier}", session=session)

    async def get_market_info(self, session=None) -> dict:
        return await self.simple_get_info_request(
            f"https://market.yandex.ru/user/{self.identifier}/reviews", session=session
        )

    async def get_o_info(self, session=None) -> dict:
        return await self.simple_get_info_request(f"http://o.yandex.ru/profile/{self.identifier}/", session=session)


class YaMessengerGuid(IdTypeInfoAggregator):
    acceptable_fields = ("yandex_messenger_guid",)

    @classmethod
    def validate_id(cls, name, identifier):
        return len(identifier) == 36 and "-" in identifier and name in cls.acceptable_fields

    async def get_messenger_info(self, session: ClientSession = None) -> dict:
        url = "https://yandex.ru/messenger/api/registry/api/"
        data = {"method": "get_users_data", "params": {"guids": [self.identifier]}}
        async with session.post(
            url, headers=HEADERS, cookies=self.cookies, data={"request": (None, json.dumps(data))}
        ) as response:
            text = await response.text()
            # r = requests.post(url, headers=HEADERS, cookies=self.cookies, files={'request': (None, json.dumps(data))})
            info = extract(text)
            if info:
                info["URL"] = f"https://yandex.ru/chat#/user/{self.identifier}"
        return info


async def crawl(user_data: dict, cookies: dict = None, checked_values: list = None, info_data: dict = None):
    entities = (YaUsername, YaPublicUserId, YaMessengerGuid)
    if cookies is None:
        cookies = {}
    if checked_values is None:
        checked_values = []
    for k, v in user_data.items():
        values = list(v) if isinstance(v, set) else [v]
        for value in values:
            if value in checked_values:
                continue

            for e in entities:
                if not e.validate_id(k, value):
                    continue

                checked_values.append(value)

                # print(f"[*] Get info by {k} `{value}`...\n")
                entity_obj = e(value, cookies)
                await entity_obj.collect()
                # pprint(entity_obj.sites_results)
                # entity_obj.print()
                info_data[f"[*] Get info by {k} `{value}`..."].update(**entity_obj.sites_results)
                await crawl(entity_obj.info, cookies, checked_values, info_data)
    return info_data


def pretty_view(data):
    answer = ""

    for by, sites_results in data.items():
        answer += f"\n{by}\n"
        for sitename, data in sites_results.items():

            if not data:
                # answer += "\n\tNot found.\n"
                continue
            answer += f"\n[+] Yandex.{sitename.capitalize()}"

            if "URL" in data:
                answer += f'\n\tURL: {data.get("URL")}'
            for k, v in data.items():
                if k != "URL":
                    answer += f"\n\t{k.capitalize()}: {v}"
            answer += "\n"
    return answer


async def get_yandex_account_info(username: str) -> str:
    user_data = {"username": username.split("@")[0]}
    info_data = collections.defaultdict(dict)
    try:
        return pretty_view(await crawl(user_data, cookies, info_data=info_data))
    except Exception as e:
        logger.warning(e)
        return str(e)


def main():
    # identifier_type = "username"
    #
    # if len(sys.argv) > 1:
    #     identifier = sys.argv[1]
    #     if len(sys.argv) > 2:
    #         identifier_type = sys.argv[2]
    # else:
    #     identifier = input("Enter Yandex username / login / email: ")
    #
    if not cookies:
        print(f"Cookies not found, but are required for some sites. See README to learn how to use cookies.")
    #
    # user_data = {identifier_type: identifier.split("@")[0]}
    user_data = {"username": "ecnymlo"}
    info_data = collections.defaultdict(dict)
    res = asyncio.get_event_loop().run_until_complete(crawl(user_data, cookies, info_data=info_data))
    # res = asyncio.run(crawl(user_data, cookies, info_data={}))
    pprint(res)
    print(pretty_view(res))


if __name__ == "__main__":
    main()
    # asyncio.run(get_yandex_account_info("lala@gmail.com"), )
