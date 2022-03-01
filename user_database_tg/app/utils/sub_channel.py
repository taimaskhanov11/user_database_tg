from user_database_tg.config.config import TempData
from user_database_tg.db.models import SubscriptionChannel


async def init_sub_channel():
    TempData.SUB_CHANNEL = await SubscriptionChannel.first()
