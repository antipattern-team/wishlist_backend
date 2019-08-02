import asyncio
import aiohttp
import time

from utils import *
from workers import *
from parser import Parser, parser_factory
from db import DB, db_factory


class Crawler:
    def __init__(self, root: str, parser: Parser, fps: int,
                 pg_db: DB, es_db: DB, pg_host: str, es_host: str, es_coll, pg_db_name, pg_db_user, pg_db_pass,
                 debug: bool, filename: str = 'db.txt'):
        self._root: str = root
        self._parser: Parser = parser
        self._fps: int = fps
        self._pg_db: DB = pg_db
        self._es_db: DB = es_db
        self._pg_host: str = pg_host
        self._es_host: str = es_host
        self._es_coll: str = es_coll
        self._pg_db_name: str = pg_db_name
        self._pg_db_user: str = pg_db_user
        self._pg_db_pass: str = pg_db_pass
        self._debug: bool = debug
        self._file: str = filename
        self._net_sess: aiohttp.ClientSession = None

    async def _init_conns(self):
        self._net_sess = aiohttp.ClientSession()
        if not await self._es_db.connect(self._es_host):
            raise ConnectionError('Couldn\'t connect to es')
        if not await self._pg_db.connect(host=self._pg_host, user=self._pg_db_user,
                                         password=self._pg_db_pass, database=self._pg_db_name):
            raise ConnectionError('Couldn\'t connect to pg')

    async def _reset_db(self):
        await self._es_db.drop(self._es_coll)
        await self._pg_db.drop(self._es_coll)

    def _reset_file(self):
        with open(self._file, 'w'):
            pass

    async def run(self):
        await self._init_conns()

        if self._debug:
            self._reset_file()

        to_middleware = asyncio.Queue()
        to_fetchers = asyncio.Queue()
        to_saver = asyncio.Queue()

        counter = Counter()
        idx_counter = Counter()
        idle_counter = IdleCounter()

        await to_middleware.put(self._root)
        await self._reset_db()

        coros = [
            middleware(to_middleware, to_fetchers, self._fps, counter, idle_counter),
            reseter(counter),
            idler(idle_counter),

            *[fetcher(to_fetchers, to_middleware, to_saver, self._parser)
              for _ in range(20)],

            *[saver([self._es_db, self._pg_db], self._es_coll, to_saver, idx_counter, True)
              for _ in range(4)]
        ]

        await asyncio.gather(*coros)


if __name__ == '__main__':
    root = 'https://m2.ikea.com/ru/ru/cat/tovary-functional/'
    parser = parser_factory('IKEA')
    es = db_factory('Elasticsearch')
    pg = db_factory('Postgres')

    sleep = get_env('SLEEP', False)
    fps = get_env('FPS', 10)
    debug = get_env('DEBUG', True)
    filename = get_env('DFILE', 'db.txt')

    es_host = get_env('ESHOST', 'localhost')
    es_coll = get_env('ESCOLL', 'products')

    pg_host = get_env('PGHOST', 'localhost')
    pg_database = get_env('POSTGRES_DB', 'wishlist')
    pg_password = get_env('POSTGRES_PASSWORD', '')
    pg_user = get_env('POSTGRES_USER', 'postgres')

    if sleep:
        secs = 60
        print(f'Sleeping for {secs} secs')
        time.sleep(secs)
        print('Slept')

    crawler = Crawler(root=root, parser=parser, fps=fps,
                      es_db=es, pg_db=pg, es_host=es_host, pg_host=pg_host,
                      es_coll=es_coll, pg_db_name=pg_database, pg_db_user=pg_user, pg_db_pass=pg_password,
                      debug=debug, filename=filename)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.run())

