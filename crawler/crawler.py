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
                 db: DB, db_host: str, debug: bool, filename: str = 'db.txt'):
        self._name = name
        self._root = root
        self._parser = parser
        self._fps = fps
        self._db = db
        self._db_host = db_host
        self._debug = debug
        self._file = filename
        self._net_sess = None

    def _init_conns(self):
        self._net_sess = aiohttp.ClientSession()
        self._db.connect(self._db_host)

    async def _reset_db(self):
        await self._db.drop(self._name)

    def _reset_file(self):
        with open(self._file, 'w'):
            pass

    async def run(self):
        self._init_conns()

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

            saver(self._db, 'ikea', to_saver, idx_counter, True),
            saver(self._db, 'ikea', to_saver, idx_counter, True),
            saver(self._db, 'ikea', to_saver, idx_counter, True),
        ]

        await asyncio.gather(*coros)


def main():
    name = 'ikea'
    root = 'https://m2.ikea.com/ru/ru/cat/tovary-functional/'
    parser = parser_factory('IKEA')
    db = db_factory('Elasticsearch')

    db_host = 'localhost'
    try:
        db_host = os.environ['DBHOST']
    except KeyError:
        pass

    fps = 10
    try:
        fps = int(os.environ['FPS'])
    except KeyError:
        pass

    debug = True
    try:
        debug = bool(os.environ['DEBUG'])
    except KeyError:
        pass

    filename = 'db.txt'
    try:
        filename = bool(os.environ['DFILE'])
    except KeyError:
        pass

    crawler = Crawler(name=name, root=root, parser=parser, fps=fps,
                      db=db, db_host=db_host, debug=debug, filename=filename)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.run())


if __name__ == '__main__':

    sleep = False
    try:
        sleep = os.environ['SLEEP']
    except KeyError:
        pass

    if sleep:
        time.sleep(10)
        print('Slept')

    main()
