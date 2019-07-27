import time
from aiohttp import web
import aiohttp_cors
from routes import routes
from auth_client import AuthRpcClient
from models import Manage
from settings import *

if __name__ == '__main__':
    if sleep:
        secs = 60
        print(f'Sleeping for {secs} secs')
        time.sleep(secs)
        print('Slept')

    async def on_startup(app):
        await Manage.init_conn(user=pg_user, password=pg_password,
                               database=pg_database, host=pg_host)
        app.auth_connection = await AuthRpcClient().connect(
            host=rmq_host,
        )

    app = web.Application()
    app.on_startup.append(on_startup)

    for method, route, handler, name in routes:
        app.router.add_route(method, route, handler, name=name)

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=['GET', 'POST', 'DELETE']
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    web.run_app(app, host='0.0.0.0', port=8080)
