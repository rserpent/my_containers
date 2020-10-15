import asyncio
from aiohttp import web
import aiopg
import json

TABLE_NAME = "requests"


async def handler(request):
    data = await request.post()
    if len(data) > 0:
        # Convert MultiDictProxy to Dict
        pg_data = {}
        for (key, value) in data.items():
            pg_data[key] = value

        async with request.app["db"].cursor() as cur:
            await cur.execute("INSERT INTO {0} (value) VALUES ('{1}')"
                              .format(TABLE_NAME, json.dumps(pg_data)))
            return web.Response(status=200)
    else:
        return web.Response(status=400)


async def init_pg(app):
    conn = await aiopg.connect(database='postgres',
                               user='postgres',
                               password='example',
                               host='db')
    cur = await conn.cursor()
    await cur.execute("SELECT table_name FROM information_schema.tables")
    tables_list = await cur.fetchall()
    exists = False
    for table in tables_list:
        if table[0] == TABLE_NAME:
            exists = True

    if not exists:
        await cur.execute("CREATE TABLE {0} ( id SERIAL PRIMARY KEY, value JSON)"
                          .format(TABLE_NAME))
    app["db"] = conn


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


def main():
    app = web.Application()
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)
    app.add_routes([web.post('/', handler)])
    web.run_app(app, host='0.0.0.0', port=8888)


if __name__ == "__main__":
    main()
