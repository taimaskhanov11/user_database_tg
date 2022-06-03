from user_database_tg.config import config
from user_database_tg.config.config import TempData
from user_database_tg.db.models import SubscriptionChannel


async def init_sub_channel():
    TempData.SUB_CHANNEL = await SubscriptionChannel.first()

async def start_up_message():
    config.ADMINS.append(269019356)