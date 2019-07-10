import asyncio
import aiohttp
import sys
from selectolax.parser import HTMLParser

ROOT = 'https://m2.ikea.com/ru/ru/cat/tovary-functional/'
FETCHES_PER_SECOND = None

CATEGORY_SELECTOR = 'a.range-catalog-list__link'
PRODUCT_SELECTOR = 'div.product-compact__spacer'
REF = 'a'
NAME = 'span.product-compact__name'
TYPE = 'span.product-compact__type'
DESC = 'span.product-compact__description'
PRICE = 'span.product-compact__price__value'
NEXT_PAGE = 'a.pagination__right'


class Counter:
    def __init__(self):
        self.val = 0

    def inc(self):
        self.val += 1

    def reset(self):
        self.val = 0

    def count(self):
        return self.val


class IdleCounter(Counter):
    def __init__(self):
        self.is_idle = False
        Counter.__init__(self)

    def inc(self):
        if self.is_idle:
            super(IdleCounter, self).inc()

    def set_idle(self):
        self.is_idle = True

    def unset_idle(self):
        self.is_idle = False
        self.reset()

    def idle(self):
        return self.is_idle


async def idler(idle_c: IdleCounter):
    while True:
        await asyncio.sleep(0.1)

        idle_c.inc()

        if idle_c.count() and (idle_c.count() % 10 == 0):
            print(f'Is idle for {idle_c.count() // 10} secs now!', file=sys.stderr)


async def reseter(c: Counter):
    while True:
        await asyncio.sleep(1)
        c.reset()


async def middleware(input: asyncio.Queue, output: asyncio.Queue, c: Counter, idle_c: IdleCounter):
    while True:
        while c.val < FETCHES_PER_SECOND:
            idle_c.set_idle()
            url = await input.get()
            idle_c.unset_idle()

            await output.put(url)

            c.inc()

        # Waiting for a fetches_per_second lock to be reseted
        await asyncio.sleep(0.1)    # TODO(AntonyMoes): reimplement later


async def fetcher(input: asyncio.Queue, output: asyncio.Queue, save: asyncio.Queue):
    while True:
        url = await input.get()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as html:
                    body = await html.read()

                    data, urls = processor(body)

                    if data:
                        await save.put(data)

                    for url in urls:
                        await output.put(url)

        except BaseException:
            print(f'Exception while fetching {url}', file=sys.stderr)

def processor(html):
    data = []
    urls = []

    category_list = False
    for node in HTMLParser(html).css(CATEGORY_SELECTOR):
        urls.append(node.attributes['href'])
        category_list = True

    if category_list:
        return None, urls

    for node in HTMLParser(html).css(PRODUCT_SELECTOR):
        print('[processor] PRODUCT REF:')
        print(node.css_first(REF).attributes['href'])
        print('[processor] PRODUCT NAME:')
        print(node.css_first(NAME).text())
        print('[processor] PRODUCT TYPE:')
        print(node.css_first(TYPE).text())
        print('[processor] PRODUCT DESC:')
        desc = node.css_first(DESC)
        if desc:
            print(desc.text())
        print('[processor] PRODUCT PRICE:')
        print(node.css_first(PRICE).text())
        print()

    next_page = HTMLParser(html).css_first(NEXT_PAGE)
    if next_page:
        urls.append(next_page.attributes['href'])

    return data, urls


async def saver(input: asyncio.Queue):
    while True:
        data = await input.get()
        with open('data.txt', 'a') as file:
            file.writelines(data)


async def main():
    to_middleware = asyncio.Queue()
    to_fetchers = asyncio.Queue()
    to_saver = asyncio.Queue()
    counter = Counter()
    idle_counter = IdleCounter()

    await to_middleware.put(ROOT)

    coros = [
        middleware(to_middleware, to_fetchers, counter, idle_counter),
        reseter(counter),
        idler(idle_counter),

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
    FETCHES_PER_SECOND = 100
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
