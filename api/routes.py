from view_handlers import Gifts, Products, Friends, Wishlist, User


routes = [
    ('GET', '/products',         Products, 'products'),
    ('GET', '/products/popular', Products, 'popular'),
    ('GET', '/products/search',  Products, 'products.search'),
    ('GET', '/friends',          Friends,  'friends'),
    ('GET', '/friends/search',   Friends,  'friends.search'),
    ('GET', '/gifts/{name}',     Gifts,    'gifts'),
    ('*',   '/wishlist',         Wishlist, 'wishlist'),
    ('*',   '/id/{name}',        User,     'id'),
]