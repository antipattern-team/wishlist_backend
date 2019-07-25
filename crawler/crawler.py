import asyncio
import aiohttp
import os
import time

from utils import Counter, IdleCounter
from workers import *
from parser import Parser, parser_factory
from db import DB, db_factory


class Crawler:
    def __init__(self, name: str, root: str, parser: Parser, fps: int,
                 pg_db: DB, es_db: DB, pg_host: str, es_host: str, pg_db_name, pg_db_pass,
                 debug: bool, filename: str = 'db.txt'):
        self._name: str = name
        self._root: str = root
        self._parser: Parser = parser
        self._fps: int = fps
        self._pg_db: DB = pg_db
        self._es_db: DB = es_db
        self._pg_host: str = pg_host
        self._es_host: str = es_host
        self._pg_db_name: str = pg_db_name
        self._pg_db_pass: str = pg_db_pass
        self._debug: bool = debug
        self._file: str = filename
        self._net_sess: aiohttp.ClientSession = None

    async def _init_conns(self):
        self._net_sess = aiohttp.ClientSession()
        if not await self._es_db.connect(self._es_host):
            raise ConnectionError('Couldn\'t connect to es')
        if not await self._pg_db.connect(host=self._es_host, user='postgres',
                                         password=self._pg_db_pass, database=self._pg_db_name):
            raise ConnectionError('Couldn\'t connect to pg')

    async def _reset_db(self):
        await self._es_db.drop(self._name)
        await self._pg_db.drop(self._name)

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

            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),
            fetcher(to_fetchers, to_middleware, to_saver, self._parser),

            saver([self._es_db, self._pg_db], self._name, to_saver, idx_counter, True),
            saver([self._es_db, self._pg_db], self._name, to_saver, idx_counter, True),
            saver([self._es_db, self._pg_db], self._name, to_saver, idx_counter, True),
            saver([self._es_db, self._pg_db], self._name, to_saver, idx_counter, True),
        ]

        await asyncio.gather(*coros)


def main():
    name = 'products'
    root = 'https://m2.ikea.com/ru/ru/cat/tovary-functional/'
    parser = parser_factory('IKEA')
    es = db_factory('Elasticsearch')
    pg = db_factory('Postgres')

    es_host = 'localhost'
    if 'ESHOST' in os.environ:
        es_host = os.environ['ESHOST']

    pg_host = 'localhost'
    if 'PGHOST' in os.environ:
        pg_host = os.environ['PGHOST']

    pg_database = 'wishlist'
    if 'POSTGRES_DATABASE' in os.environ:
        pg_database = os.environ['POSTGRES_DATABASE']

    pg_password = ''
    if 'POSTGRES_PASSWORD' in os.environ:
        pg_password = os.environ['POSTGRES_PASSWORD']

    fps = 10
    if 'FPS' in os.environ:
        fps = int(os.environ['FPS'])

    debug = True
    if 'DEBUG' in os.environ:
        debug = bool(os.environ['DEBUG'])

    filename = 'db.txt'
    if 'DFILE' in os.environ:
        filename = bool(os.environ['DFILE'])

    crawler = Crawler(name=name, root=root, parser=parser, fps=fps,
                      es_db=es, pg_db=pg, es_host=es_host, pg_host=pg_host,
                      pg_db_name=pg_database, pg_db_pass=pg_password,
                      debug=debug, filename=filename)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.run())


if __name__ == '__main__':

    sleep = False
    try:
        sleep = os.environ['SLEEP']
    except KeyError:
        pass

    if sleep:
        secs = 60
        print(f'Sleeping for {secs} secs')
        time.sleep(secs)
        print('Slept')

    main()
