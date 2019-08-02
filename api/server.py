import time
from aiohttp import web
from routes import routes
from auth_client import AuthRpcClient
from models import Manage
from models import *
from utils import get_env
from elastic import Elastic

if __name__ == '__main__':
    debug = get_env('DEBUG', False)
    sleep = get_env('SLEEP', False)

    es_host = get_env('ESHOST', 'localhost')
    es_coll = get_env('ESCOLL', 'products')

    pg_host = get_env('PGHOST', 'localhost')
    pg_database = get_env('POSTGRES_DB', 'wishlist')
    pg_password = get_env('POSTGRES_PASSWORD', '')
    pg_user = get_env('POSTGRES_USER', 'postgres')

    rmq_host = get_env('RMQHOST', 'localhost')

    if sleep:
        secs = 65
        print(f'Sleeping for {secs} secs')
        time.sleep(secs)
        print('Slept')

    async def on_startup(app):
        Elastic.init(es_host, es_coll)

        await Manage.init_conn(user=pg_user, password=pg_password,
                               database=pg_database, host=pg_host)

        app.auth_connection = await AuthRpcClient().connect(host=rmq_host)

        if debug:
            try:
                await User.objects.create(uid=90000, vkid='generic_test_user')
                await User.objects.create(uid=90001, vkid='generic_test_user1')
            except User.UniqueViolation:
                pass

            try:
                await Elastic.save(coll='friends', obj={'name': 'generic test user', 'fid': 90001, 'vkid': 'generic_test_user'}, id=90000)
                await Elastic.save(coll='friends', obj={'name': 'generic test user 1', 'fid': 90000, 'vkid': 'generic_test_user1'}, id=90001)

                await Friend.objects.create(uid=90000, fid=90001)
                await Friend.objects.create(uid=90001, fid=90000)

            except Friend.UniqueViolation:
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

    app.secret = get_env('APPSECRET', '123')

    for method, route, handler, name in routes:
        app.router.add_route(method, route, handler, name=name)

    web.run_app(app, host='0.0.0.0', port=8080)
