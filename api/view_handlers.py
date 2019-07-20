from aiohttp import web


def redirect(request, router_name):
    url = request.app.router[router_name].url_for()
    raise web.HTTPFound(url)


class Redirect(web.View):
    async def get(self):
        redirect(self.request, 'home')


class Home(web.View):
    async def get(self):
        return web.Response(text="HELLO")


class Products(web.View):
    # 1) Популярные товары '/products/popular'
    # 2) Товары все '/products/'
    # 2.1) Товары по поисковому запросу '/products/search'
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
    # 3) Список друзей (у которых есть вишлист) '/friends'
    # 4) Друзья по поисковому запросу '/friends/search'
    async def get(self):
        return web.Response(text="list_friends\r\n")


class Gifts(web.View):
    # 5) Что я забронировал для дарения '/gifts'
    async def get(self):
        return web.Response(
            text="Hello {}!\r\n".format(self.request.match_info['name'])
        )


class Wishlist(web.View):
    # 6) Что я хочу (и что забронировали у меня) '/wishlist'(?hui=zabronirovali)
    async def get(self):
        return web.Response(text="list_reserved\r\n")

    # 1) Добавить в вишлист '/wishlist'
    async def post(self):
        return web.Response(text="post\r\n")

    # 2) Удалить из вишлиста '/wishlist'
    async def delete(self):
        return web.Response(text="delete\r\n")


class User(web.View):
    # 7) Что хочет определенный человек (его профиль) (и что забронировали)
    # '/id/{name}' (?hui=zabronirovali)
    async def get(self):
        return web.Response(text="Hello {}\r\n".format(
            self.request.app.router['id'].url_for(name='guest'))
        )

    # 3) Забронировать '/id/{name}'
    async def post(self):
        return web.Response(text="post\r\n")

    # 4) Разбронировать '/id/{name}'
    async def delete(self):
        return web.Response(text="delete\r\n")

