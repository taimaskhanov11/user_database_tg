import asyncio

import aiohttp
from aiohttp import ClientSession

from user_database_tg.config.config import NGROCK_API

API_SERVER = None

headers = {
    'Authorization': f'Bearer {NGROCK_API}',
    'Ngrok-Version': '2',
    "Content-Type": "application/json"
}
url = "https://api.ngrok.com/tunnels"


async def request(session: ClientSession, url):
    async with session.get(url) as res:
        return await res.json()


async def get_server_host():
    global API_SERVER
    async with aiohttp.ClientSession(headers=headers, ) as session:
        res = await request(session, url)
        while not res["tunnels"]:
            res = await request(session, url)
            await asyncio.sleep(1)
    API_SERVER = res["tunnels"][0]["public_url"]


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(get_server_host())
