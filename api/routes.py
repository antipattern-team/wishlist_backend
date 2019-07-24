from handlers import *


routes = [
    ('GET',    '/products/popular', get_products_popular,    'popular'),
    ('GET',    '/friends/list',     get_friends,             'friends'),
    ('GET',    '/friends/search',   get_friends_search,      'friends_search'),
    ('GET',    '/gifts',            get_gifts,               'gifts'),
    ('GET',    '/wishlist',         get_wishlist,            'get_wishlist'),
    ('POST',   '/wishlist',         add_to_wishlist,         'add_to_wishlist'),
    ('DELETE', '/wishlist',         delete_from_wishlist,    'delete_from_wishlist'),
    ('GET',    '/wishlist/{uid}',   get_user_wishlist,       'get_user_wishlist'),
    ('POST',   '/wishlist/{uid}',   reserve_gift_for_user,   'reserve_gift_for_user'),
    ('DELETE', '/wishlist/{uid}',   cancel_gift_for_user,    'cancel_gift_for_user'),
]
