import asyncio
import html
import re
# import urllib

import aiohttp.helpers

# from mtranslate import translate
from loguru import logger

agent = {'User-Agent':
             "Mozilla/4.0 (\
    compatible;\
    MSIE 6.0;\
    Windows NT 5.1;\
    SV1;\
    .NET CLR 1.1.4322;\
    .NET CLR 2.0.50727;\
    .NET CLR 3.0.04506.30\
    )"}


async def translate(field, to_translate, to_language="auto", from_language="auto"):
    to_translate = aiohttp.helpers.quote(to_translate)
    link = f"http://translate.google.com/m?tl={to_language}&sl={from_language}&q={to_translate}"
    async with aiohttp.ClientSession(headers=agent) as session:
        async with session.get(link) as response:
            data = await response.text()
            expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
            re_result = re.findall(expr, data)
            result = html.unescape(re_result[0]) if re_result else ""
            # return result
            return {field: result}


if __name__ == '__main__':
    asyncio.run(translate("Hi as >< 🙋‍ П ", "ru"))
