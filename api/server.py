import os
import time
from aiohttp import web
import aiohttp_cors
from routes import routes
from models import *

if __name__ == '__main__':
    debug = False
    if 'DEBUG' in os.environ:
        debug = bool(os.environ['DEBUG'])

    sleep = False
    if 'SLEEP' in os.environ:
        sleep = bool(os.environ['SLEEP'])

    es_host = 'localhost'
    if 'ESHOST' in os.environ:
        es_host = os.environ['ESHOST']

    pg_host = 'localhost'
    if 'PGHOST' in os.environ:
        pg_host = os.environ['PGHOST']

    pg_database = 'wishlist'
    if 'POSTGRES_DB' in os.environ:
        pg_database = os.environ['POSTGRES_DB']

    pg_password = ''
    if 'POSTGRES_PASSWORD' in os.environ:
        pg_password = os.environ['POSTGRES_PASSWORD']

    pg_user = 'postgres'
    if 'POSTGRES_USER' in os.environ:
        pg_user = os.environ['POSTGRES_USER']

    if sleep:
        secs = 65
        print(f'Sleeping for {secs} secs')
        time.sleep(secs)
        print('Slept')

    async def on_startup(app):
        await Manage.init_conn(user=pg_user, password=pg_password,
                               database=pg_database, host=pg_host)

        if debug:
            try:
                await User.objects.create(uid=90000, vkid='generic_test_user')
                await User.objects.create(uid=90001, vkid='generic_test_user1')
            except User.UniqueViolation:
                pass

            try:
                await Product.objects.create(pid=90000, name='generic_test_product',
                                             reference='generic_test_reference',
                                             image='generic_test_image', price=1000)

            except Product.UniqueViolation:
                pass

            try:
                await Wants.objects.create(id=90000, uid=90000, pid=90000, gid=90001)
            except Wants.UniqueViolation:
                pass

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
