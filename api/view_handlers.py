from aiohttp import web


class Products(web.View):
    # 1) '/products/popular'
    # 2) '/products/'
    # 2.1) '/products/search'
    async def get(self):
        data = {
            'products': {
                'a': {
                    'price': 100,
                },
                'b': {
                    'price': 250,
                }
            }
        }
        return web.json_response(data)


class Friends(web.View):
    # 3) '/friends'
    # 4) '/friends/search'
    async def get(self):
        return web.Response(text="list_friends\r\n")


class Gifts(web.View):
    # 5) '/gifts' what I reserved for giving
    async def get(self):
        return web.Response(
            text="Hello {}!\r\n".format(self.request.match_info['name'])
        )


class Wishlist(web.View):
    # 6) '/wishlist'
    async def get(self):
        return web.Response(text="list_reserved\r\n")

    # 1) '/wishlist' add to
    async def post(self):
        return web.Response(text="post\r\n")

    # 2) '/wishlist' remove from
    async def delete(self):
        return web.Response(text="delete\r\n")


class User(web.View):
    # 7) '/id/{name}' someone's wishlist
    async def get(self):
        return web.Response(text="Hello {}\r\n".format(
            self.request.app.router['id'].url_for(name='guest'))
        )

    # 3) '/id/{name}' reserve gift
    async def post(self):
        return web.Response(text="post\r\n")

    # 4) '/id/{name}' remove gift
    async def delete(self):
        return web.Response(text="delete\r\n")
