from aiohttp import web
from routes import routes
from orm.orm import Manage
from auth_client import AuthRpcClient
import os

if __name__ == '__main__':

    app = web.Application()

    pg_host = 'localhost'
    if 'PGHOST' in os.environ:
        pg_host = os.environ['PGHOST']

    pg_database = 'wishlist'
    if 'POSTGRES_DATABASE' in os.environ:
        pg_database = os.environ['POSTGRES_DATABASE']

    pg_password = ''
    if 'POSTGRES_PASSWORD' in os.environ:
        pg_password = os.environ['POSTGRES_PASSWORD']

    rmq_host = 'localhost'
    if 'RMQHOST' in os.environ:
        rmq_host = os.environ['RMQHOST']

    rmq_login = 'guest'
    if 'RMQ_LOGIN' in os.environ:
        pg_host = os.environ['RMQ_LOGIN']

    rmq_password = 'guest'
    if 'RMQ_PASSWORD' in os.environ:
        rmq_password = os.environ['RMQ_PASSWORD']

    server_port = 8080
    if 'SERVER_PORT' in os.environ:
        pg_database = os.environ['SERVER_PORT']

    app.auth_key = '123'
    if 'AUTH_KEY' in os.environ:
        app.auth_key = bool(os.environ['AUTH_KEY'])


    async def on_startup(app: web.Application):
        await Manage.init_conn(
            user='postgres',
            password=pg_password,
            database=pg_database,
            host=pg_host
        )
        app.auth_connection = await AuthRpcClient().connect(
            host=rmq_host,
            port=5672,
            login=rmq_login,
            password=rmq_password,
        )

    app.on_startup.append(on_startup)

    # route part
    for method, route, handler, name in routes:
        app.router.add_route(method, route, handler, name=name)
    web.run_app(
        app,
        port=server_port
    )
