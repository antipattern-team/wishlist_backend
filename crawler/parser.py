from selectolax.parser import HTMLParser


class Parser:
    def parse(self, body: bytes) -> (list, list):
        pass


class IKEAParser(Parser):
    def __init__(self):
        self._s_category = 'a.range-catalog-list__link'
        self._s_product = 'div.product-compact__spacer'
        self._s_ref = 'a'
        self._s_img = 'img'
        self._s_name = 'span.product-compact__name'
        self._s_type = 'span.product-compact__type'
        self._s_desc = 'span.product-compact__description'
        self._s_price = 'span.product-compact__price__value'
        self._s_next = 'a.pagination__right'

    def parse(self, body: bytes) -> (list, list):
        data = []
        urls = []

        category_list = False
        for node in HTMLParser(body).css(self._s_category):
            urls.append(node.attributes['href'])
            category_list = True

        if category_list:
            return None, urls

        for node in HTMLParser(body).css(self._s_product):
            product = dict()

            product['reference'] = node.css_first(self._s_ref).attributes['href']
            product['image'] = node.css_first(self._s_img).attributes['src']
            product['name'] = node.css_first(self._s_name).text()

            tp = node.css_first(self._s_type).text()
            tp = tp.split('\n')
            tp = [el.strip() for el in tp if el.strip() is not '']
            tp = ' '.join(tp)
            product['product_type'] = tp

            desc = node.css_first(self._s_desc)
            if desc:
                desc = desc.text()

            product['description'] = desc or ''
            product['price'] = node.css_first(self._s_price).text()

            data.append(product)

        next_page = HTMLParser(body).css_first(self._s_next)
        if next_page:
            urls.append(next_page.attributes['href'])

        return data, urls


def parser_factory(name: str) -> Parser or None:
    if name == 'IKEA':
        return IKEAParser()

    return None
