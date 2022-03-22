import asyncio
import datetime

from user_database_tg.db.db_main import init_tortoise
from user_database_tg.db.models import Subscription, DbUser, Payment


async def add_db_lost_data():
    # if TEST:
    #     await init_tortoise(host="localhost", password="postgres")
    # else:
    #     await init_tortoise(host="localhost")
    await init_tortoise(host="95.105.113.65", db_name="users_database", password="Tel993917.")

    data = [
        "1,1 месяц  (лимит 25 запросов в сутки) - 35р.,true,true,2022-04-17 04:55:44.785005 +00:00,30,25,22",
        "2,1 месяц  (лимит 100 запросов в сутки) - 100р,true,true,2022-04-18 10:46:22.657766 +00:00,30,100,98",
        "3,1 месяц  (лимит 25 запросов в сутки) - 35р.,true,true,2022-04-16 15:39:49.846341 +00:00,30,25,12",
        "4,12 месяцев (лимит 25 запросов в сутки) - 350р,true,false,2023-03-17 15:49:39.056538 +00:00,365,25,25",
        "5,6 месяцев  (лимит 25 запросов в сутки) - 200р,true,true,2022-09-15 08:12:13.132578 +00:00,180,25,14",
        "6,1 месяц  (лимит 100 запросов в сутки) - 100р,true,true,2022-04-16 14:14:32.033259 +00:00,30,100,100",
        "7,1 месяц  (лимит 25 запросов в сутки) - 35р.,true,false,2022-04-16 14:31:45.140227 +00:00,30,25,25",
        "8,1 месяц  (без ограничения) - 500р,true,true,2022-04-16 14:03:07.480696 +00:00,30,,",
        "9,1 месяц  (лимит 25 запросов в сутки) - 35р.,true,false,2022-04-16 22:11:50.592421 +00:00,30,25,25",
        "10,1 месяц  (без ограничения) - 500р,true,false,2022-04-18 05:39:23.360868 +00:00,30,,",
        "11,12 месяцев (лимит 25 запросов в сутки) - 350р,true,false,2023-03-18 18:06:40.318635 +00:00,365,25,25",
        "12,1 месяц  (лимит 25 запросов в сутки) - 35р.,true,false,2022-04-15 06:34:02.586343 +00:00,30,25,25",
        "13,1 месяц  (лимит 25 запросов в сутки) - 35р.,true,true,2022-04-16 15:41:50.247390 +00:00,30,25,9",
        "14,1 месяц  (лимит 25 запросов в сутки) - 35р.,true,false,2022-04-16 17:13:31.859998 +00:00,30,25,25",
        "15,Тестовая на 12 месяцев(Безлимит) 1р,true,true,2022-03-05 06:02:15.572491 +00:00,1,,",
        "16,1 месяц  (лимит 25 запросов в сутки) - 35р.,true,true,2022-04-17 13:47:25.525912 +00:00,30,25,20",
        "17,6 месяцев  (лимит 100 запросов в сутки) - 550р,true,false,2022-09-14 23:31:04.560880 +00:00,180,100,100",
    ]

    for elem in data:
        elem = elem.split(",")
        # time_string = "06/05/2020 12:06:58"
        # print(data[3])
        # print(dateparser.parse(data[3]))
        # exit()
        print(elem[4])
        print(elem[4][:-14])
        duration = datetime.datetime.strptime(elem[4][:-14], "%Y-%m-%d %H:%M:%S")
        print(duration)
        print(elem)
        # continue
        s = await Subscription.create(
            title=elem[1],
            is_subscribe=elem[2],
            is_paid=elem[3],
            duration=duration,
            days_duration=elem[5],
            daily_limit=elem[6] or None,
            remaining_daily_limit=elem[7] or None,
        )
    users = [
        "1,502706323,OlesyZol,russian,false,2022-03-18 04:54:53.566666 +00:00,1",
        "2,1258138257,wmcpcfsx,russian,false,2022-03-18 20:35:16.807221 +00:00,2",
        "3,1346751195,username_groos,russian,false,2022-03-17 15:33:28.964089 +00:00,3",
        "4,741936072,GirlAgen,russian,false,2022-03-19 06:58:47.569357 +00:00,5",
        "5,765193190,CaHeK80,russian,false,2022-03-17 14:10:13.809689 +00:00,6",
        "6,588511882,sumatoreo,russian,false,2022-03-17 14:00:00.164630 +00:00,8",
        "7,731008342,CoderCriminal,russian,false,2022-03-17 00:49:52.223646 +00:00,9",
        "9,1412561451,Khizhnyak_Alexey,russian,false,2022-03-18 13:46:38.934602 +00:00,17",
        "8,2014301618,chief_MailLeaks,russian,false,2022-03-03 17:34:39.926543 +00:00,15",
    ]
    for elem in users:
        elem = elem.split(",")
        duration = datetime.datetime.strptime(elem[5][:-14], "%Y-%m-%d %H:%M:%S")
        sub = await Subscription.get(pk=elem[6])
        s = await DbUser.create(
            user_id=elem[1],
            username=elem[2],
            subscription=sub,
            language=elem[3],
            is_search=elem[4],
            register_data=duration,
        )
        print(s)

    payments = [
        "1,2022-03-18 04:58:32.609129 +00:00,35,1",
        "2,2022-03-19 10:50:14.602652 +00:00,100,2",
        "3,2022-03-17 15:46:16.158256 +00:00,35,3",
        "4,2022-03-19 08:13:25.706195 +00:00,200,4",
        "5,2022-03-17 14:15:15.811063 +00:00,100,5",
        "6,2022-03-17 14:05:37.106815 +00:00,500,6",
        "7,2022-03-17 15:46:39.903085 +00:00,35,7",
        "8,2022-03-18 13:48:52.830534 +00:00,35,8",
    ]
    for elem in payments:
        elem = elem.split(",")
        db_user = await DbUser.get(pk=elem[3])
        duration = datetime.datetime.strptime(elem[1][:-14], "%Y-%m-%d %H:%M:%S")
        await Payment.create(
            db_user=db_user,
            date=duration,
            amount=elem[2],
        )


if __name__ == "__main__":
    asyncio.run(add_db_lost_data())
