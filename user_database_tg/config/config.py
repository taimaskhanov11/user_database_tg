# from environs import Env
import os
from distutils.util import strtobool

from pyqiwip2p.AioQiwip2p import AioQiwiP2P
from dotenv import load_dotenv, dotenv_values
load_dotenv()
# env = Env()
# env.read_env()
config = dotenv_values(".env")

TG_TOKEN = os.getenv("TG_TOKEN")
QIWI_TOKEN = os.getenv("QIWI_TOKEN")
TEST = strtobool(os.getenv("TEST"))
p2p = AioQiwiP2P(auth_key=QIWI_TOKEN)
