import asyncio
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from user_database_tg.app.filters.bot_settings import EditUserFilter, EditUserFilterAPI
from user_database_tg.app.markups import bot_settings_markup, admin_menu
from user_database_tg.app.utils.daily_processes import delete_api_token
from user_database_tg.app.utils.payment_processes import add_api_token
from user_database_tg.config.config import TempData
from user_database_tg.db.models import (
    DbUser,
    Limit,
    Payment,
    SubscriptionChannel,
)
from user_database_tg.loader import bot


class GetUserInfoStates(StatesGroup):
    start = State()


class EditUserSubStates(StatesGroup):
    start = State()
    end = State()


class EditUserSubAPIStates(StatesGroup):
    start = State()
    end = State()


class EditChannelStates(StatesGroup):
    start = State()


async def get_bot_info(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    users_count = await DbUser.all().count()
    # last_reg_users_obj = "\n".join([f"@{us.username}" for us in Limit.new_users_in_last_day_obj])
    last_reg_users = ""
    for i in range(10):
        try:
            user = Limit.new_users_in_last_day_obj.pop()
            user_info = f"@{user.username if user.username != 'НЕ УКАЗАН' else user.user_id}\n"
            if user_info not in last_reg_users:
                last_reg_users += user_info
        except Exception as e:
            logger.trace(e)
            break
    # last_pay_users = "\n".join(Limit.last_pay_users)

    payments = await Payment.all().order_by("-date").limit(10).select_related("db_user")
    last_pay_users = ""
    for p in payments:
        last_pay_users += f"@{p.db_user.user_id if p.db_user.username == 'НЕ УКАЗАН' else p.db_user.username}|{p.date.replace(microsecond=0)}|{p.amount}р\n"
    answer = (
        f"Количество запросов к бд за последние сутки:\n{Limit.number_day_requests}\n"
        f"___________________\n"
        f"Всего пользователей:\n{users_count}\n"
        f"___________________\n"
        f"Новых пользователей за последние сутки:\n{Limit.new_users_in_last_day}\n"
        f"___________________\n"
        f"10 последних зарегистрировавшихся пользователей:\n{last_reg_users}\n"
        f"___________________\n"
        f"Сумма поступивших платежей за последние сутки:\n{Limit.lats_day_amount_payments}\n"
        f"___________________\n"
        f"Платежи за последние сутки:\n{last_pay_users}\n"
    )
    await call.message.answer(answer)


async def get_all_users(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    db_users = await DbUser.all()
    users = ""
    for user in db_users:
        user_info = f"@{user.username if user.username != 'НЕ УКАЗАН' else user.user_id}\n"
        if user_info not in users:
            users += user_info

    if len(users) > 4096:
        for x in range(0, len(users), 4096):
            await call.message.answer(users[x: x + 4096])
    else:
        await call.message.answer(users)


async def get_user_info_start(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("Ведите имя пользователя или id")
    await GetUserInfoStates.start.set()


@logger.catch
async def get_user_info_end(message: types.Message, state: FSMContext):
    field = message.text
    field = field[1:] if message.text[0] == "@" else field
    if field[0].isdigit() or field[0].isalpha():
        search_field = {"user_id": int(field)} if field[0].isdigit() else {"username": field}

        # user: DbUser = await DbUser.get_or_none(**search_field).select_related("subscription").prefetch_related(
        #     "payments")
        try:
            user: DbUser = await DbUser.filter(**search_field).select_related("subscription").prefetch_related(
                "payments").first()

        except Exception as e:
            logger.critical(e)
            await message.answer("Некорректное имя пользователя или id")
            return

        if not user:
            await message.answer("Некорректное имя пользователя или id")
            return
        # user: DbUser = await DbUser.get(**search_field).select_related("subscription")
        # payments: list[Payment] = await DbUser.payments.all()
        logger.info(user.payments)
        # payments: list[Payment] = user.payments
        # payments_str = "DATETIME                   AMOUNT\n"
        payments_str = ""
        # "✓2022-03-01 22:39:00+00:00 "
        for pay in user.payments:
            payments_str += f"{pay.date.replace(microsecond=0)} - {pay.amount}р\n"
        user_data = (
            f"🔑 ID: {user.user_id}\n"
            f"👤 Логин: @{user.username}\n"
            f"Подписка: {user.subscription.title}\n"
            f"Совершенные платежи:\n{payments_str or 'Пусто'}\n"
        )

        user_data2 = (
            f"API PROFILE\n"
            f"Подписка: {user.subscription.title}\n"
        )
        await message.answer(user_data, reply_markup=bot_settings_markup.get_edit_user(user.user_id))
        await message.answer(user_data2, reply_markup=bot_settings_markup.get_edit_user_api(user.user_id))

        await state.finish()
    else:
        await message.answer("Некорректное имя пользователя или id")


async def edit_user_sub(call: types.CallbackQuery, state: FSMContext):
    user_id = int(re.findall(r"edit_user_(\d*)", call.data)[0])
    await state.update_data(user_id=user_id)
    db_user = await DbUser.filter(user_id=user_id).select_related("subscription").first()
    # subscription = await Subscription.get(db_user=db_user)
    await call.message.answer(
        f"🔑 ID: {db_user.user_id}\n" f"👤 Логин: @{db_user.username}\n" f"Подписка:\n{db_user.subscription}",
        reply_markup=admin_menu.change_user_sub_field
        # f"{subscription}", reply_markup=admin_menu.change_field
    )
    await state.update_data(db_user=db_user)
    await EditUserSubStates.first()


async def edit_user_sub_start(call: types.CallbackQuery, state: FSMContext):
    field = call.data
    await state.update_data(field=field)
    await call.message.answer(f"Введите новое значения для поля {field}")
    await EditUserSubStates.next()


@logger.catch
async def edit_user_sub_end(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        db_user: DbUser = data["db_user"]
        field = data["field"]
        await db_user.subscription.refresh_from_db()
        new_value = message.text
        if message.text == "Unlimited":
            new_value = None
        # elif field == "daily_limit":
        #     new_value = int(new_value)
        #     setattr(db_user.subscription, "remaining_daily_limit", new_value)

        setattr(db_user.subscription, field, new_value)
        db_user.subscription.is_subscribe = True
        await db_user.subscription.save()
        await message.answer(f"Данные подписки изменены")

        await message.answer(
            f"🔑 ID: {db_user.user_id}\n" f"👤 Логин: @{db_user.username}\n" f"Подписка:\n{db_user.subscription}",
            reply_markup=admin_menu.change_user_sub_field,
        )
        # await state.finish()
        await EditUserSubStates.first()

    except Exception as e:
        logger.critical(e)
        await message.answer("Ошибка! Неправильный ввод")


async def edit_user_sub_api(call: types.CallbackQuery, state: FSMContext):
    user_id = int(re.findall(r"edit_user_api_(\d*)", call.data)[0])
    await state.update_data(user_id=user_id)
    db_user = await DbUser.filter(user_id=user_id).first().select_related("api_subscription")
    # subscription = await Subscription.get(db_user=db_user)
    await call.message.answer(
        f"🔑 ID: {db_user.user_id}\n" f"👤 Логин: @{db_user.username}\n" f"Подписка:\n{db_user.api_subscription}",
        reply_markup=admin_menu.change_user_sub_field
        # f"{subscription}", reply_markup=admin_menu.change_field
    )
    await state.update_data(db_user=db_user)
    await EditUserSubAPIStates.first()


async def edit_user_sub_start_api(call: types.CallbackQuery, state: FSMContext):
    field = call.data
    await state.update_data(field=field)
    await call.message.answer(f"Введите новое значения для поля {field}")
    await EditUserSubAPIStates.next()


@logger.catch
async def edit_user_sub_end_api(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        db_user: DbUser = data["db_user"]
        field = data["field"]
        await db_user.api_subscription.refresh_from_db()
        new_value = message.text
        if message.text == "Unlimited":
            new_value = None
        # elif field == "daily_limit":
        #     new_value = int(new_value)
        #     setattr(db_user.subscription, "remaining_daily_limit", new_value)
        if field == "days_duration":
            if not db_user.api_subscription.days_duration:
                if int(new_value) > 0:
                    asyncio.create_task(add_api_token(db_user.api_subscription.token))

            elif int(new_value) == 0 or int(new_value) < 0:
                asyncio.create_task(delete_api_token(db_user.api_subscription.token))

        setattr(db_user.api_subscription, field, new_value)
        await db_user.api_subscription.save()
        await message.answer(f"Данные подписки изменены")

        await message.answer(
            f"🔑 ID: {db_user.user_id}\n" f"👤 Логин: @{db_user.username}\n" f"Подписка:\n{db_user.api_subscription}",
            reply_markup=admin_menu.change_user_sub_field,
        )
        # await state.finish()
        await EditUserSubAPIStates.first()

    except Exception as e:
        logger.critical(e)
        await message.answer("Ошибка! Неправильный ввод")


async def sub_channel_status(call: types.CallbackQuery):
    await call.message.delete()
    channel = (
        f"Канал для подписки @{TempData.SUB_CHANNEL.chat_id}" if TempData.SUB_CHANNEL else "Нет группы для подписки"
    )
    channel_check = ""
    if TempData.SUB_CHANNEL:
        channel_check = (
            f"Проверка подписки включена" if TempData.SUB_CHANNEL.checking else "Проверка подписки отключена"
        )
    await call.message.answer(f"{channel}\n{channel_check}", reply_markup=bot_settings_markup.channel_status)


async def edit_sub_channel_status(call: types.CallbackQuery):
    if TempData.SUB_CHANNEL.checking is False:
        TempData.SUB_CHANNEL.checking = True
    else:
        TempData.SUB_CHANNEL.checking = False

    channel = (
        f"Канал для подписки @{TempData.SUB_CHANNEL.chat_id}" if TempData.SUB_CHANNEL else "Нет группы для подписки"
    )
    channel_check = f"Проверка подписки включена" if TempData.SUB_CHANNEL.checking else "Проверка подписки отключена"
    if TempData.SUB_CHANNEL:
        await TempData.SUB_CHANNEL.save()

    await call.message.answer(
        f"Статус подписки изменен\n{channel}\n{channel_check}",
        reply_markup=bot_settings_markup.channel_status,
    )


async def change_sub_channel_start(call: types.CallbackQuery):
    await call.message.answer(
        "Ведите новую ссылку на бота в таком формате\n:" "https://t.me/try_bot_mind или @try_bot_mind или id"
    )
    await EditChannelStates.start.set()


@logger.catch
async def change_sub_channel_end(message: types.Message, state: FSMContext):
    try:
        chat_id = message.text
        if chat_id[0].isdigit():
            chat_id = int(chat_id)
        elif chat_id[0] == "@":
            pass
        else:
            re_chat_id = re.findall(r"https://t.me/(.*)", chat_id)
            if re_chat_id:
                chat_id = re_chat_id[0]
            chat_id = f"@{chat_id}"

        chat_info = await bot.get_chat(
            chat_id=chat_id,
        )

        if TempData.SUB_CHANNEL is not None:
            await TempData.SUB_CHANNEL.delete()
        TempData.SUB_CHANNEL = await SubscriptionChannel.create(
            chat_id=chat_info["username"],
        )

        channel = (
            f"Канал для подписки @{TempData.SUB_CHANNEL.chat_id}" if TempData.SUB_CHANNEL else "Нет группы для подписки"
        )
        channel_check = ""
        if TempData.SUB_CHANNEL:
            channel_check = (
                f"Проверка подписки включена" if TempData.SUB_CHANNEL.checking else "Проверка подписки отключена"
            )
        await message.answer(
            f"Данные обновлены\n{channel}\n{channel_check}",
            reply_markup=bot_settings_markup.channel_status,
        )
        await state.finish()

    except Exception as e:
        logger.critical(e)
        await message.answer("Ошибка")


def register_bot_info_handler(dp: Dispatcher):
    dp.register_callback_query_handler(get_bot_info, text="bot_info", state="*")
    dp.register_callback_query_handler(get_all_users, text="all_users", state="*")
    dp.register_callback_query_handler(get_user_info_start, text="user_info", state="*")
    dp.register_message_handler(get_user_info_end, state=GetUserInfoStates.start)

    dp.register_callback_query_handler(edit_user_sub_api, EditUserFilterAPI())
    dp.register_callback_query_handler(edit_user_sub_start_api, state=EditUserSubAPIStates.start)
    dp.register_message_handler(edit_user_sub_end_api, state=EditUserSubAPIStates.end)

    dp.register_callback_query_handler(edit_user_sub, EditUserFilter())
    dp.register_callback_query_handler(edit_user_sub_start, state=EditUserSubStates.start)
    dp.register_message_handler(edit_user_sub_end, state=EditUserSubStates.end)

    dp.register_callback_query_handler(sub_channel_status, text="sub_channel_status")
    dp.register_callback_query_handler(edit_sub_channel_status, text="change_sub_status")
    dp.register_callback_query_handler(change_sub_channel_start, text="change_sub_channel")
    dp.register_message_handler(change_sub_channel_end, state=EditChannelStates.start)
