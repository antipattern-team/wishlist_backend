from handlers import *


routes = [
    ('GET',    '/products/search/{name}',   get_products_search,     'products_search'),
    ('GET',    '/products/popular',         get_products_popular,    'products_popular'),
    ('GET',    '/friends/list',             get_friends,             'friends'),
    ('GET',    '/friends/search/{name}',    get_friends_search,      'friends_search'),
    ('GET',    '/gifts',                    get_gifts,               'gifts'),
    ('GET',    '/wishlist',                 get_wishlist,            'wishlist'),
    ('POST',   '/wishlist',                 add_to_wishlist,         'wishlist_add'),
    ('DELETE', '/wishlist',                 delete_from_wishlist,    'wishlist_remove'),
    ('GET',    '/wishlist/{vkid}',          get_user_wishlist,       'user_wishlist'),
    ('POST',   '/wishlist/{vkid}',          reserve_gift_for_user,   'user_gift_add'),
    ('DELETE', '/wishlist/{vkid}',          cancel_gift_for_user,    'user_gift_remove'),
]
