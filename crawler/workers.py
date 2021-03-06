import asyncio
import aiohttp
from typing import List
import re

from utils import Counter, IdleCounter
from parser import Parser
from db import DB


async def idler(idle_c: IdleCounter) -> None:
    while True:
        await asyncio.sleep(0.1)

        idle_c.inc()

        if idle_c.count() and (idle_c.count() % 10 == 0):
            print(f'Is idle for {idle_c.count() // 10} secs now!')


async def reseter(c: Counter) -> None:
    time = 0
    while True:
        await asyncio.sleep(1)
        c.reset()

        time += 1
        if time and (time % 10 == 0):
            print(f'Working for {time} secs now!')


async def middleware(input: asyncio.Queue, output: asyncio.Queue, fps: int, c: Counter, idle_c: IdleCounter) -> None:
    while True:
        while c.count() < fps:
            '''On counter reset get queue size in case of unhandled urls'''
            if c.count() == 0:
                c.set(output.qsize())

            idle_c.set_idle()
            url = await input.get()
            idle_c.unset_idle()

            await output.put(url)

            c.inc()

        # Waiting for a fetches_per_second lock to be reseted
        await asyncio.sleep(0.1)    # TODO(AntonyMoes): reimplement later


async def fetcher(input: asyncio.Queue, output: asyncio.Queue, save: asyncio.Queue, parser: Parser) -> None:
    while True:
        url = await input.get()

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as html:
                body = await html.read()

                data, urls = parser.parse(body)

                if data:
                    await save.put(data)

                for url in urls:
                    await output.put(url)


async def saver(dbs: List[DB], coll: str, input: asyncio.Queue, idx_c: Counter,
                debug: bool = False, save_file: str = 'db.txt') -> None:
    price_re = re.compile("[0-9]+")

    while True:
        data = await input.get()
        for product in data:
            idx_c.inc()
            count = idx_c.count()

            product['price'] = int(price_re.match(product['price'].replace(" ", "")).group(0))

            if debug:
                with open(save_file, 'a') as file:
                    file.write(f'Entry {count}:\n')
                    for key, line in product.items():
                        file.write(f'{key}: {line}\n')
                    file.write('\n')
            for db in dbs:
                await db.save(product, coll, count)
