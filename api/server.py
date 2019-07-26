import os
import time
from aiohttp import web
from routes import routes
from models import Manage

if __name__ == '__main__':
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
        secs = 60
        print(f'Sleeping for {secs} secs')
        time.sleep(secs)
        print('Slept')

    async def on_startup(app):
        await Manage.init_conn(user=pg_user, password=pg_password,
                               database=pg_database, host=pg_host)

    app = web.Application()
    app.on_startup.append(on_startup)

    for method, route, handler, name in routes:
        app.router.add_route(method, route, handler, name=name)
    web.run_app(app, host='0.0.0.0', port=8080)
