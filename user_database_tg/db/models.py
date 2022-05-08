import secrets
from datetime import datetime, timedelta

from aiogram import types
from loguru import logger
from tortoise import fields, models

from user_database_tg.config import config
from user_database_tg.config.config import TZ

__all__ = [
    "DbUser",
    "Subscription",
    "Billing",
    "DbTranslation",
    "SubscriptionInfo",
    "Limit",
    "Payment",
    "SubscriptionChannel",
    "dig_file_HackedUser",
    "sym_file_HackedUser",
    "HackedUser",
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
    "q_HackedUser",
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


class HackedUser(models.Model):
    email = fields.CharField(max_length=255, index=True)
    password = fields.CharField(max_length=255)
    service = fields.CharField(max_length=255)

    # async def filter(self):
    #     pass
    #
    # class Meta:
    #     abstract = True


# class Limit(models.Model):
#     number_day_requests = fields.IntField()
#     new_in_last_day = fields.IntField()
#     amount_payments = fields.IntField()

# class ApiSubscription():
#     user = fields.OneToOneField("models.DbUser", on_delete=fields.CASCADE, null=True)
#     duration = fields.IntField(default=0)
#
#
# class ApiSubscriptionInfo():
#     title = fields.CharField(255)
#     price = fields.IntField()
#     duration = fields.IntField(default=0)
#     daily_limit = fields.IntField(null=True)
#
#     def __str__(self):
#         return (
#             f"Название : {self.title}\n"
#             f"Цена: {self.price}\n"
#             f"Количество дней: {self.duration}\n"
#         )


class DbTranslation(models.Model):  # todo 2/26/2022 4:40 PM taima:
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

    # search
    wait_search = fields.TextField()
    data_not_found = fields.TextField()
    daily_limit_ended = fields.TextField()
    left_attempts = fields.TextField()

    # pay
    create_payment = fields.TextField()
    wait_payment = fields.TextField()
    go_payment_b = fields.CharField(max_length=255)
    payment_not_found = fields.TextField()

    accept_payment = fields.TextField()
    accept_payment_b = fields.CharField(max_length=255)
    reject_payment = fields.TextField()
    reject_payment_b = fields.CharField(max_length=255)

    subscribe_channel = fields.TextField()

    def __str__(self):
        return (
            f"*Основное меню:\n"
            f"⭕1. Стартовое сообщение:\n{self.start_message}\n"
            f"⭕2. Профиль:\n{self.profile}\n"
            f"⭕3. Описание:\n{self.description}\n"
            f"⭕4. Поддержка:\n{self.support}\n"
            f"⭕5. Купить:\n{self.subscribe}\n"
            f"⭕6. Кнопка Профиль:\n{self.profile_b}\n"
            f"⭕7. Кнопка Описание:\n{self.description_b}\n"
            f"⭕8. Кнопка Поддержка:\n{self.support_b}\n"
            f"⭕9. Кнопка Купить:\n{self.subscribe_b}\n\n"
            f""
            f"*Меню поиска: \n"
            f"⭕10.Ожидание поиска:\n{self.wait_search}\n"
            f"⭕11.Данные не найдены:\n{self.data_not_found}\n"
            f"⭕12.Дневной лимит закончен:\n{self.daily_limit_ended}\n"
            f"⭕13.Запросов осталось:\n{self.left_attempts}\n\n"
            f"*Меню Оплаты\n"
            f""
            f"⭕14. Счет создан:\n{self.create_payment}\n"
            f"⭕15. Ожидание оплаты:\n{self.wait_payment}\n"
            f"⭕16. Кнопка оплатить:\n{self.go_payment_b}\n"
            f"⭕17. Платеж не найден:\n{self.payment_not_found}\n"
            f"⭕18. Подписка оплачена:\n{self.accept_payment}\n"
            f"⭕19. Кнопка я оплатил:\n{self.accept_payment_b}\n"
            f"⭕20. Подписка отменена:\n{self.reject_payment}\n"
            f"⭕21. Кнопка отмены подписки:\n{self.reject_payment_b}\n\n"
            f"* Подписка на канал\n"
            f"⭕21. Подписка на канал:\n {self.subscribe_channel}"
        )


class SubscriptionChannel(models.Model):
    chat_id = fields.CharField(max_length=255)
    checking = fields.BooleanField(default=False)

    def __str__(self):
        return f"{self.chat_id}"


class SubscriptionInfo(models.Model):
    title = fields.CharField(max_length=255)
    price = fields.IntField()
    days = fields.IntField()
    daily_limit = fields.IntField(null=True)

    def __str__(self):
        return (
            # f"ID: {self.pk}\n"
            f"Название : {self.title}\n"
            f"Цена: {self.price}\n"
            f"Количество дней: {self.days}\n"
            f"Дневной лимит запросов: {self.daily_limit}"
        )


class Subscription(models.Model):
    title = fields.CharField(max_length=255, default="Нет подписки")
    is_subscribe = fields.BooleanField(default=False)
    is_paid = fields.BooleanField(default=True)
    # duration = fields.IntField(default=0)
    duration = fields.DatetimeField()
    days_duration = fields.IntField(default=0)
    daily_limit = fields.IntField(default=config.DAILY_LIMIT, null=True)
    remaining_daily_limit = fields.IntField(default=config.DAILY_LIMIT, null=True)
    db_user: "DbUser"

    def __str__(self):
        return (
            # f"ID: {self.pk}\n"
            f"Название : {self.title}\n"
            f"Количество дней: {self.days_duration}\n"
            f"Дневной лимит запросов: {self.daily_limit}\n"
            f"Оставшийся дневной лимит: {self.remaining_daily_limit} "
        )

    async def decr(self):
        if self.daily_limit is not None:
            self.remaining_daily_limit -= 1
            await self.save()


class ApiSubscription(Subscription):
    db_user: 'DbUser' = fields.OneToOneField("models.DbUser", null=True, related_name="api_subscription")
    token = fields.CharField(32, default=secrets.token_hex(16))

    def __str__(self):
        return (
            # f"ID: {self.pk}\n"
            f"Название : {self.title}\n"
            f"Количество дней: {self.days_duration}\n"
            f"Дневной лимит запросов: Unlimited\n"
            # f"Оставшийся дневной лимит: {self.remaining_daily_limit} "
        )


class ApiSubscriptionInfo(SubscriptionInfo):
    pass


class DbUser(models.Model):
    user_id = fields.BigIntField(index=True)
    username = fields.CharField(max_length=255)
    subscription: Subscription = fields.OneToOneField("models.Subscription", related_name="db_user")
    language = fields.CharField(max_length=20, null=True, default=None)
    is_search = fields.BooleanField(default=False)
    register_data = fields.DatetimeField()
    payments: "Payment"
    api_subscription: ApiSubscription

    # translation = None

    async def __aenter__(self):
        # Включение режима блокировки пока запрос не завершиться
        self.is_search = True
        await self.save()
        return self

    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Отключение режима поиска
        self.is_search = False
        await self.save()
        if exc_type:
            logger.exception(f"{exc_type}, {exc_val}, {exc_tb}")

    @classmethod
    async def new(cls, message: types.Message):
        pass

    @classmethod
    # @logger.catch
    async def get_or_new(cls, user_id, username) -> "DbUser":
        try:
            user = await cls.filter(user_id=user_id).select_related("subscription", "api_subscription").first()
            # logger.info(user)
        except Exception as e:
            user = None
            logger.critical(e)
        is_created = False
        if not user.api_subscription:
            await ApiSubscription.create(
                duration=datetime.now(TZ),
                db_user=user
            ),
            await user.refresh_from_db()
            await user.fetch_related("api_subscription")
        if not user:
            # duration = datetime.now(TZ)
            # duration = datetime.now(TZ) + timedelta(days=2)
            if not username:
                username = "НЕ УКАЗАН"
            user = await cls.create(
                user_id=user_id,
                username=username,
                subscription=await Subscription.create(
                    duration=datetime.now(TZ),
                ),
                register_data=datetime.now(TZ),
            )
            await ApiSubscription.create(
                duration=datetime.now(TZ),
                db_user=user
            )
            await user.refresh_from_db()
            await user.fetch_related("api_subscription")

            is_created = True
            Limit.new_users_in_last_day += 1
            Limit.new_users_in_last_day_obj.append(user)

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


class Payment(models.Model):
    db_user: DbUser = fields.ForeignKeyField("models.DbUser", related_name="payments")
    date = fields.DatetimeField()
    amount = fields.IntField()


class Limit:
    number_day_requests = 0
    new_users_in_last_day = 0
    lats_day_amount_payments = 0
    new_users_in_last_day_obj: list = []
    last_pay_users = []
    API_SERVER = None
    @classmethod
    def daily_process(cls):
        Limit.number_day_requests = 0
        Limit.new_users_in_last_day = 0
        Limit.new_users_in_last_day_obj = []
        Limit.lats_day_amount_payments = 0


class Billing(models.Model):
    db_user: DbUser = fields.OneToOneField(
        "models.DbUser",
    )
    # bill_id = fields.BigIntField(index=True)
    bill_id = fields.IntField(index=True)
    amount = fields.IntField()
    subscription = fields.OneToOneField("models.Subscription")

    @classmethod
    async def create_bill(cls, db_user, bill_id, sub_info: SubscriptionInfo):
        subscription = await Subscription.create(
            title=sub_info.title,
            is_subscribe=True,
            is_paid=False,
            duration=datetime.now(TZ) + timedelta(int(sub_info.days)),
            days_duration=sub_info.days,
            daily_limit=sub_info.daily_limit,
            remaining_daily_limit=sub_info.daily_limit,
        )
        return await cls.create(
            db_user=db_user,
            bill_id=bill_id,
            amount=sub_info.price,
            subscription=subscription,
        )


class APIBilling(models.Model):
    db_user: DbUser = fields.OneToOneField(
        "models.DbUser",
    )
    # bill_id = fields.BigIntField(index=True)
    bill_id = fields.IntField(index=True)
    amount = fields.IntField()
    api_subscription: ApiSubscription = fields.OneToOneField("models.ApiSubscription")

    @classmethod
    async def create_bill(cls, db_user, bill_id, sub_info: ApiSubscriptionInfo):
        subscription = await ApiSubscription.create(
            title=sub_info.title,
            is_subscribe=True,
            is_paid=False,
            duration=datetime.now(TZ) + timedelta(int(sub_info.days)),
            days_duration=sub_info.days,
            daily_limit=sub_info.daily_limit,
            remaining_daily_limit=sub_info.daily_limit,
            # db_user=db_user,
        )
        # print(dict(subscription))
        # subscription.db_user = db_user
        # await subscription.save()
        return await cls.create(
            db_user=db_user,
            bill_id=bill_id,
            amount=sub_info.price,
            api_subscription=subscription,
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
