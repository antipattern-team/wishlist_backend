from aiohttp import web
from auth import authorize_from_vk
from view_handlers import Home, Gifts, Products, Friends, Wishlist, User, Redirect


routes = [
    ('GET', '/',                 Home,     'home'),
    ('GET', '/products',         Products, 'products'),
    ('GET', '/products/popular', Products, 'popular'),
    ('GET', '/products/search',  Products, 'products.search'),
    ('GET', '/friends',          Friends,  'friends'),
    ('GET', '/friends/search',   Friends,  'friends.search'),
    ('GET', '/gifts/{name}',     Gifts,    'gifts'),
    ('*',   '/wishlist',         Wishlist, 'wishlist'),
    ('*',   '/id/{name}',        User,     'id'),
    ('*',   '/{any}',            Redirect, 'redir')
]