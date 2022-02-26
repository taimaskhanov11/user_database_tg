from datetime import datetime, timedelta

from aiogram import types
from loguru import logger
from tortoise import fields, models

from user_database_tg.app.markups import subscribe


class HackedUser():
    email = fields.CharField(max_length=255, index=True)
    password = fields.CharField(max_length=255)
    service = fields.CharField(max_length=255)


class Subscription(models.Model):
    title = fields.CharField(max_length=255, default="Нет подписки")
    is_subscribe = fields.BooleanField(default=False)
    is_paid = fields.BooleanField(default=True)
    # duration = fields.IntField(default=0)
    duration = fields.DatetimeField(auto_now_add=True)
    day_limit = fields.IntField(default=3, null=True)


class DbUser(models.Model):
    user_id = fields.IntField(index=True)
    username = fields.CharField(max_length=255)
    subscription = fields.OneToOneField("models.Subscription")
    language = fields.CharField(max_length=20, null=True, default=None)
    is_search = fields.BooleanField(default=False)

    @classmethod
    async def new(cls, message: types.Message):
        pass

    # @classmethod
    # @logger.catch
    # async def get_or_new(cls, user_id, username) -> 'User':
    #     user = await cls.get_or_none(user_id=user_id).select_related("subscription")
    #     await cls.get_or_create()
    #     is_created = False
    #     if not user:
    #         user = await cls.create(
    #             user_id=user_id,
    #             username=username,
    #             subscription=await Subscription.create(
    #
    #             ),
    #         )
    #         is_created = True
    #     if is_created:
    #         logger.info(f"Создание нового пользователя {user_id} {username}")
    #     return user

    @classmethod
    @logger.catch
    async def get_or_new(cls, user_id, username) -> 'DbUser':
        user, is_created = await cls.get_or_create(
            user_id=user_id,
            defaults={
                "username": username,
                "subscription": await Subscription.create()
            }
        )
        if is_created:
            logger.info(f"Создание нового пользователя {user_id} {username}")
        return user


class Billing(models.Model):
    user = fields.OneToOneField("models.DbUser")
    # bill_id = fields.BigIntField(index=True)
    bill_id = fields.IntField(index=True)
    amount = fields.IntField()
    subscription = fields.OneToOneField("models.Subscription")

    @classmethod
    async def create_receipt(cls, user, bill_id, amount, duration, day_limit):
        # перевод месяца в дни
        days = int(duration) * 30

        if day_limit == "n":
            day_limit = None
        subscription = await Subscription.create(
            title=f"{duration} мес({day_limit or 'Безлимит'} в сутки) {amount}р",
            is_subscribe=True,
            is_paid=False,
            duration=datetime.today() + timedelta(days),
            day_limit=day_limit,
        )
        await cls.create(
            user=user,
            bill_id=bill_id,
            amount=amount,
            subscription=subscription
        )


def create_alphabet_tables():
    for sign in list('abcdefghijklmnopqrstuvwxyz'):
        class_name = f"{sign}_HackedUser"
        new_class = type(class_name, (models.Model,), {
            "email": fields.CharField(max_length=255, index=True),
            "password": fields.CharField(max_length=255),
            "service": fields.CharField(max_length=255),
        })
        globals()[class_name] = new_class
        # locals()[class_name] = new_class
    for class_name in (f"dig_file_HackedUser", "sym_file_HackedUser"):
        new_class = type(class_name, (models.Model,), {
            "email": fields.CharField(max_length=255, index=True),
            "password": fields.CharField(max_length=255),
            "service": fields.CharField(max_length=255),
        })
        globals()[class_name] = new_class


create_alphabet_tables()

__all__ = [
    "DbUser",
    "Subscription",
    "Billing",
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
