import asyncio
import aiohttp
import sys
from selectolax.parser import HTMLParser
from elasticsearch_async import AsyncElasticsearch

ROOT = 'https://m2.ikea.com/ru/ru/cat/tovary-functional/'
FETCHES_PER_SECOND = None

CATEGORY_SELECTOR = 'a.range-catalog-list__link'
PRODUCT_SELECTOR = 'div.product-compact__spacer'
REF = 'a'
IMG = 'img'
NAME = 'span.product-compact__name'
TYPE = 'span.product-compact__type'
DESC = 'span.product-compact__description'
PRICE = 'span.product-compact__price__value'
NEXT_PAGE = 'a.pagination__right'

SAVE_FILE = 'db.txt'

client = AsyncElasticsearch(hosts=['localhost'])


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
    time = 0
    while True:
        await asyncio.sleep(1)
        c.reset()

        time += 1
        if time and (time % 10 == 0):
            print(f'Working for {time} secs now!', file=sys.stderr)


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
    async with aiohttp.ClientSession() as session:
        while True:
            url = await input.get()

            # try:
            async with session.get(url) as html:
                body = await html.read()

                data, urls = processor(body)

                if data:
                    await save.put(data)

                for url in urls:
                    await output.put(url)

            # except BaseException:
            #     print(f'Exception while fetching {url}', file=sys.stderr)


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
        product = dict()
        # product.append(node.css_first(REF).attributes['href'])
        product['reference'] = node.css_first(REF).attributes['href']
        # product.append(node.css_first(IMG).attributes['src'])
        product['image'] = node.css_first(IMG).attributes['src']
        # product.append(node.css_first(NAME).text())
        product['name'] = node.css_first(NAME).text()
        tp = node.css_first(TYPE).text()
        tp = tp.split('\n')
        tp = [el.strip() for el in tp if el.strip() is not '']
        tp = ' '.join(tp)
        # product.append(tp)
        product['type'] = tp

        desc = node.css_first(DESC)
        if desc:
            desc = desc.text()

        # product.append(desc or '')
        product['description'] = desc or ''
        # product.append(node.css_first(PRICE).text())
        product['price'] = node.css_first(PRICE).text()
        data.append(product)

    next_page = HTMLParser(html).css_first(NEXT_PAGE)
    if next_page:
        urls.append(next_page.attributes['href'])

    return data, urls


async def saver(input: asyncio.Queue, idx_c: Counter):
    while True:
        data = await input.get()
        with open(SAVE_FILE, 'a') as file:
            for product in data:
                for key, line in product.items():
                    file.write(f'{key}: {line}\n')
                file.write('\n')
                idx_c.inc()
                await client.index(index='ikea', doc_type='product', id=idx_c.count(), body=product)


async def main():
    with open(SAVE_FILE, 'w'):
        pass

    to_middleware = asyncio.Queue()
    to_fetchers = asyncio.Queue()
    to_saver = asyncio.Queue()

    counter = Counter()
    idx_counter = Counter()
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

        saver(to_saver, idx_counter),
        saver(to_saver, idx_counter),
        saver(to_saver, idx_counter),
    ]

    await asyncio.gather(*coros)

if __name__ == '__main__':
    FETCHES_PER_SECOND = 10
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
