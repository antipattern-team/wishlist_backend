import asyncio
import aiohttp

ROOT = 'https://www.ikea.com/ru/ru/'
FETCHES_PER_SECOND = 10


class Counter:
    def __init__(self):
        self.val = 0

    def inc(self):
        self.val += 1

    def reset(self):
        self.val = 0


async def reseter(c: Counter):
    while True:
        await asyncio.sleep(1)
        c.reset()


async def middleware(input: asyncio.Queue, output: asyncio.Queue, c: Counter):
    while True:
        while c.val < FETCHES_PER_SECOND:
            url = await input.get()
            await output.put(url)
            c.inc()

        await asyncio.sleep(0.1)    # TODO(AntonyMoes): reimplement later


async def fetcher(input: asyncio.Queue, output: asyncio.Queue, save: asyncio.Queue):
    while True:
        url = await input.get()

        async with aiohttp.request('GET', url) as html:
            print(html)
            body = await html.read()
            print(body)

            data, urls = processor(html)
            await save.put(data)

            for url in urls:
                await output.put(url)



def processor(html):
    data = None
    urls = []
    return data, urls


async def saver(input: asyncio.Queue):
    while True:
        data = await input.get()


async def main():
    to_middleware = asyncio.Queue()
    to_fetchers = asyncio.Queue()
    to_saver = asyncio.Queue()
    counter = Counter()

    # for i in range(20):
    #     await to_middleware.put(i)
    await to_middleware.put(ROOT)

    coros = [
        middleware(to_middleware, to_fetchers, counter),
        reseter(counter),

        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),
        fetcher(to_fetchers, to_middleware, to_saver),

        saver(to_saver),
        saver(to_saver),
        saver(to_saver),
    ]

    await asyncio.gather(*coros)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
