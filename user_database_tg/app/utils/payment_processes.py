import asyncio

from user_database_tg.config.config import p2p
from user_database_tg.db.models import Billing
from user_database_tg.loader import bot


async def check_payment(bill_id, user_id):
    for _ in range(15):
        bill = await p2p.check(bill_id=bill_id)

        if bill.status == "PAID":
            db_bill = await Billing.get(bill_id).select_related("subscription")
            db_bill.user = db_bill.subscription
            await db_bill.user.save()
            await db_bill.delete()
            await bot.send_message(user_id, "Подписка успешно оплачена!")

        elif bill.status == "REJECTED":
            db_bill = await Billing.get_or_none(bill_id)
            if db_bill:
                await bot.send_message(user_id, "Подписка успешно удалена!")
                await db_bill.delete()
            await bot.send_message(user_id, "Подписка успешно отменена!")
            break
        await asyncio.sleep(60)
