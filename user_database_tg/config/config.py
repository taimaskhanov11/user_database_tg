import datetime
from pathlib import Path
from environs import Env
from pyqiwip2p.AioQiwip2p import AioQiwiP2P


env = Env()
env.read_env()

TG_TOKEN = env.str("TG_TOKEN")
QIWI_TOKEN = env.str("QIWI_TOKEN")
TEST = env.bool("TEST")
p2p = AioQiwiP2P(auth_key=QIWI_TOKEN)
TZ = datetime.timezone(datetime.timedelta(hours=3))
BASE_DIR = Path(__file__).parent.parent.parent

class TempData:
    NO_FIND_EMAIL = []
    CHECK_CHANNEL_SUBSCRIPTIONS = False
    SUB_CHANNEL = None
