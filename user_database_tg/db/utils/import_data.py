import argparse
import asyncio
import pprint

from loguru import logger

from user_database_tg.db.db_main import init_tortoise, init_logging
from user_database_tg.db.models import DbUser, Payment, Subscription


async def import_to_new_db(from_, to_):
    await init_tortoise(**from_)
    await init_tortoise(**to_)

    # await init_tortoise(host="95.105.113.65", db_name="users_database", password="Tel993917.")
    await init_tortoise(**from_)

    users: list[DbUser] = await DbUser.filter(subscription__is_subscribe=True).select_related("subscription")
    user_sub_pay: list[tuple[dict, dict, dict]] = []
    for u in users:
        # ps = []
        payments = await u.payments
        p = payments[0] if payments else None
        p_d = None
        u_d = dict(u)
        del u_d["id"]
        del u_d["subscription_id"]
        s_d = dict(u.subscription)
        del s_d["id"]

        if p:
            p_d = dict(p)
            del p_d["id"]
            del p_d["db_user_id"]

        user_sub_pay.append((u_d, s_d, p_d))

    await init_tortoise(**to_)
    for u, s, p in user_sub_pay:
        s = await Subscription.create(**s)
        u, _is_create = await DbUser.get_or_create(**u, defaults={"subscription": s})
        if _is_create:
            p = await Payment.create(**p, db_user=u)
        else:
            logger.trace(f"{u.username} уже существует")
    logger.success(f"Выгрузка из {from_['host']} в {to_['host']} успешно завершена")


def get_parser():
    parser = argparse.ArgumentParser(description="Upload data in db")
    parser.add_argument("--from_", type=str)
    parser.add_argument("--username", type=str)
    parser.add_argument("--password", type=str)
    parser.add_argument("--host", type=str)
    parser.add_argument("--port", type=str)
    parser.add_argument("--db_name", type=str)

    parser.add_argument("--to", type=str)
    parser.add_argument("--username2", type=str)
    parser.add_argument("--password2", type=str)
    parser.add_argument("--host2", type=str)
    parser.add_argument("--port2", type=str)
    parser.add_argument("--db_name2", type=str)
    return parser


def get_default_args():
    from_ = {
        "username": "postgres",
        "password": "Tel993917.",
        "host": "95.105.113.65",
        "port": 5432,
        "db_name": "users_database",
    }
    to_ = {
        "username": "postgres",
        "password": "T12345postgres",
        "host": "188.130.139.157",
        "port": 5432,
        "db_name": "users_database",
    }
    return from_, to_


def get_args_dict(args):
    from_ = {
        "username": args.username,
        "password": args.password,
        "host": args.host,
        "port": args.port,
        "db_name": args.db_name,
    }
    to_ = {
        "username": args.username2,
        "password": args.password2,
        "host": args.host2,
        "port": args.port2,
        "db_name": args.db_name2,
    }
    return from_, to_


if __name__ == '__main__':
    init_logging()
    parser = get_parser()
    args = parser.parse_args()

    if not args.from_:
        from_, to_ = get_default_args()
    else:
        from_, to_ = get_args_dict(args)
    logger.info(f"\n{pprint.pformat(from_)}")
    logger.info(f"\n{pprint.pformat(to_)}")
    asyncio.run(import_to_new_db(from_=from_, to_=to_))
