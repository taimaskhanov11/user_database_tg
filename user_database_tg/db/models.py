from datetime import datetime, timedelta

from aiogram import types
from loguru import logger
from tortoise import fields, models

from user_database_tg.config.config import TZ


class HackedUser:
    email = fields.CharField(max_length=255, index=True)
    password = fields.CharField(max_length=255)
    service = fields.CharField(max_length=255)


class DbMessage(models.Model):  # todo 2/26/2022 4:40 PM taima:
    title = fields.CharField(max_length=255)
    # text = fields.TextField()
    language = fields.CharField(max_length=20)

    # start
    start_message = fields.TextField()

    # menu
    profile = fields.TextField()
    description = fields.TextField()
    support = fields.TextField()
    subscribe = fields.TextField()

    # menu buttons
    profile_b = fields.CharField(max_length=255)
    description_b = fields.CharField(max_length=255)
    support_b = fields.CharField(max_length=255)
    subscribe_b = fields.CharField(max_length=255)

    # waiting for end search
    wait_search = fields.TextField()
    data_not_found = fields.TextField()

    # waiting for pay
    create_payment = fields.TextField()
    wait_payment = fields.TextField()
    go_payment_b = fields.CharField(max_length=255)

    reject_payment = fields.TextField()
    reject_payment_b = fields.CharField(max_length=255)


class Subscription(models.Model):
    title = fields.CharField(max_length=255, default="Нет подписки")
    is_subscribe = fields.BooleanField(default=False)
    is_paid = fields.BooleanField(default=True)
    # duration = fields.IntField(default=0)
    duration = fields.DatetimeField(auto_now_add=True)
    daily_limit = fields.IntField(default=3, null=True)
    remaining_daily_limit = fields.IntField(default=3, null=True)


class DbUser(models.Model):
    user_id = fields.IntField(index=True)
    username = fields.CharField(max_length=255)
    subscription = fields.OneToOneField("models.Subscription")
    language = fields.CharField(max_length=20, null=True, default=None)

    is_search = fields.BooleanField(default=False)

    # translation = None

    @classmethod
    async def new(cls, message: types.Message):
        pass

    @classmethod
    @logger.catch
    async def get_or_new(cls, user_id, username) -> "DbUser":
        user = await cls.get_or_none(user_id=user_id).select_related("subscription")
        is_created = False
        if not user:
            # duration = datetime.now(TZ)
            # duration = datetime.now(TZ) + timedelta(days=2)
            user = await cls.create(
                user_id=user_id,
                username=username,
                subscription=await Subscription.create(
                    # duration=duration
                ),
            )
            is_created = True
        if is_created:
            logger.info(f"Создание нового пользователя {user_id} {username}")
        return user

    # @classmethod
    # @logger.catch
    # async def get_or_new(cls, user_id, username) -> 'DbUser':
    #     user, is_created = await cls.get_or_create(
    #         user_id=user_id,
    #         defaults={
    #             "username": username,
    #             "subscription": await Subscription.create()
    #         }
    #     )
    #     if is_created:
    #         logger.info(f"Создание нового пользователя {user_id} {username}")
    #     return user


class Billing(models.Model):
    db_user = fields.OneToOneField(
        "models.DbUser",
    )
    # bill_id = fields.BigIntField(index=True)
    bill_id = fields.IntField(index=True)
    amount = fields.IntField()
    subscription = fields.OneToOneField("models.Subscription")

    @classmethod
    async def create_bill(cls, db_user, bill_id, amount, duration, daily_limit):
        # перевод месяца в дни
        days = int(duration) * 30

        if daily_limit == "n":
            daily_limit = None
        subscription = await Subscription.create(
            title=f"{duration} мес({daily_limit or 'Безлимит'} в сутки) {amount} rub",
            is_subscribe=True,
            is_paid=False,
            duration=datetime.now(TZ) + timedelta(days),
            daily_limit=daily_limit,
            remaining_daily_limit=daily_limit,
        )
        await cls.create(
            db_user=db_user, bill_id=bill_id, amount=amount, subscription=subscription
        )


def create_alphabet_tables():
    for sign in list("abcdefghijklmnopqrstuvwxyz"):
        class_name = f"{sign}_HackedUser"
        new_class = type(
            class_name,
            (models.Model,),
            {
                "email": fields.CharField(max_length=255, index=True),
                "password": fields.CharField(max_length=255),
                "service": fields.CharField(max_length=255),
            },
        )
        globals()[class_name] = new_class
        # locals()[class_name] = new_class
    for class_name in (f"dig_file_HackedUser", "sym_file_HackedUser"):
        new_class = type(
            class_name,
            (models.Model,),
            {
                "email": fields.CharField(max_length=255, index=True),
                "password": fields.CharField(max_length=255),
                "service": fields.CharField(max_length=255),
            },
        )
        globals()[class_name] = new_class


create_alphabet_tables()  # todo 2/26/2022 3:58 PM taima:

__all__ = [
    "DbUser",
    "Subscription",
    "Billing",
    "DbMessage",
    "dig_file_HackedUser",
    "sym_file_HackedUser",
    "a_HackedUser",
    "b_HackedUser",
    "c_HackedUser",
    "d_HackedUser",
    "e_HackedUser",
    "f_HackedUser",
    "g_HackedUser",
    "h_HackedUser",
    "i_HackedUser",
    "j_HackedUser",
    "k_HackedUser",
    "l_HackedUser",
    "m_HackedUser",
    "n_HackedUser",
    "o_HackedUser",
    "p_HackedUser",
    "r_HackedUser",
    "s_HackedUser",
    "t_HackedUser",
    "u_HackedUser",
    "v_HackedUser",
    "w_HackedUser",
    "x_HackedUser",
    "y_HackedUser",
    "z_HackedUser",
]
