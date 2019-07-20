from view_handlers import *


routes = [
    ('GET',    '/products/popular', get_products_popular, 'popular'),
    ('GET',    '/friends/list',     get_friends,          'friends'),
    ('GET',    '/friends/search',   get_friends_search,   'friends.search'),
    ('GET',    '/gifts',            get_gifts,            'gifts'),
    ('GET',    '/wishlist',         get_wishlist,         'wishlist_get'),
    ('POST',   '/wishlist',         post_wishlist,        'wishlist_post'),
    ('DELETE', '/wishlist',         delete_wishlist,      'wishlist_delete'),
    ('GET',    '/wishlist/{uid}',   get_user,             'user_get'),
    ('POST',   '/wishlist/{uid}',   get_user,             'user_get'),
    ('DELETE', '/wishlist/{uid}',   get_user,             'user_get'),
]
