from tortoise import Tortoise, run_async

from user_database_tg.db.models import HackedUser
from user_database_tg.utils.parsing_data import parce_datafiles


async def init_tortoise(
        username="postgres",
        password="XJjKaDgB2n",
        host="95.105.113.65",
        port=5432,
        db_name="users_database"
):
    await Tortoise.init(  # todo
        # _create_db=True,
        db_url=f'postgres://{username}:{password}@{host}:{port}/{db_name}',
        modules={'models': ['user_database_tg.db.models']}
    )
    await Tortoise.generate_schemas()


async def create_users():
    # await init_tortoise()
    await init_tortoise(host="localhost")
    users_data = parce_datafiles("/var/lib/postgresql/TO_IMPORT")
    # print(users_data)
    # exit()

    for service, data in users_data.items():
        # print(data)
        # exit()

        users_obj = [HackedUser(email=x[0], password=x[1], service=service) for x in data]
        # print(users_obj[0].service)
        # await users_obj[0].create()
        await HackedUser.bulk_create(
            users_obj
        )


if __name__ == '__main__':
    run_async(create_users())
    # asyncio.run(create_users())
