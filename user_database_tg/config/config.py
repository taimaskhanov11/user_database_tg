import datetime
from pathlib import Path

from environs import Env
from pyqiwip2p.AioQiwip2p import AioQiwiP2P

env = Env()
env.read_env()

TG_TOKEN = env.str("TG_TOKEN")
QIWI_TOKEN = env.str("QIWI_TOKEN")
TEST = env.bool("TEST")

DB_USERNAME = env.str("DB_USERNAME")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")
DB_DB_NAME = env.str("DB_DB_NAME")
MAIN_API_TOKEN = env.str("MAIN_API_TOKEN")
NGROCK_API = env.str("NGROCK_API")

CRYPTO_SHOP_ID = env.str("CRYPTO_SHOP_ID")
CRYPTO_API_KEY = env.str("CRYPTO_API_KEY")

DAILY_LIMIT = env.int("daily_limit")
ADMINS = list(map(lambda x: int(x.strip()), env.list("ADMINS")))
# if [1985947355, 2014301618]
p2p = AioQiwiP2P(auth_key=QIWI_TOKEN)
TZ = datetime.timezone(datetime.timedelta(hours=3))
BASE_DIR = Path(__file__).parent.parent.parent
CRYPTO_HEADERS = {"Authorization": f"Token {CRYPTO_API_KEY}"}
HASH_BOT = "@Hash2PassBot"

class TempData:
    NO_FIND_EMAIL = []
    SUB_CHANNEL = None
