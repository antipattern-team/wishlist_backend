from aiohttp import web
import jwt
from middleware import auth_mw
from models import *
from settings import app_secret
from vkutils import *


async def get_products_popular(request: web.Request):
    resp = list()
    # try:
    #   data = await ORM.get_all_products()
    #   for _ in data:
    #       resp.append(_)
    # except:
    #   pass
    resp.append(  # todo(UsatiyNyan): modify when ORM is ready
        {
            'ref': 'url',  # data[i].ref
            'img': 'img_url',  # data[i].img
            'name': 'name',  # data[i].name
            'type': 'type',  # data[i].type
            'descr': 'description',  # data[i].descr
            'price': 1337,  # data[i].price
        }
    )

    resp = {
        'result': 'success',
        'type': 'popular',
        'data': resp
    }

    return web.json_response(resp)


@auth_mw
async def get_friends(request: web.Request, context):
    resp = list()
    uid = request.cookies.get('id')
    # try:
    #   data = await ORM.get_friends(uid)
    #   for _ in data:
    #       resp.append(_)
    # except:
    #   pass
    resp.append(
        {
            'friend_img': 'some_url',  # data[i].img
            'friend_name': 'anonymous',  # data[i].name
        }
    )

    resp = {
        'result': 'success',
        'type': 'friends',
        'data': resp
    }
    
    return web.json_response(resp)


@auth_mw
async def get_friends_search(request: web.Request, context):
    resp = list()
    uid = request.cookies.get('id')
    keyword = request.query.get('query')
    if keyword is None:
        return await get_friends(request)
    # try:
    #   data = await ORM.get_friends_search(uid, keyword)
    #   for _ in data:
    #       resp.append(_)
    # except:
    #   resp.append('you have no friends')
    resp.append(
        {
            'friend_img': 'some_url',  # data[i].img
            'friend_name': 'anonymous',  # data[i].name
        }
    )

    resp = {
        'result': 'success',
        'type': 'friends_search',
        'data': resp
    }

    return web.json_response(resp)


@auth_mw
async def get_gifts(request: web.Request, context):
    resp = list()
    gid = request.cookies.get('id')
    # try:
    #   data = await ORM.get_gifts(gid)
    #   for _ in data:
    #       resp.append(_)
    # except:
    #   resp.append('no gifts reserved')
    resp.append(  # todo(UsatiyNyan): consult with Max about API's response
        {
            'friend_img': 'some_url',  # data.users[i].img
            'friend_name': 'anonymous',  # data.users[i].name
            'gifts': [
                {
                    'ref': 'url',  # product.ref
                    'img': 'img_url',  # product.img
                    'name': 'name',  # product.name
                    'type': 'type',  # product.type
                    'descr': 'description',  # product.descr
                    'price': 1337,  # product.price
                }
            ]
        }
    )

    resp = {
        'result': 'success',
        'type': 'gifts',
        'data': resp
    }
    
    return web.json_response(resp)


@auth_mw
async def get_wishlist(request: web.Request, context):
    resp = list()
    uid = request.cookies.get('id')
    keyword = request.query.get('query')  # 'reserved=-1', 'unreserved=1', 'all=0'
    # try
    # if keyword is reserved: data = await ORM.get_wishlist(uid).filter('gid', None, ops.ne)
    # if keyword is unreserved: data = await ORM.get_wishlist(uid).filter('gid', None, ops.eq)
    # if keyword is all: data = await ORM.get_wishlist(uid).get('gid')
    resp.append(
        {
            'ref': 'url',  # product.ref
            'img': 'img_url',  # product.img
            'name': 'name',  # product.name
            'type': 'type',  # product.type
            'descr': 'description',  # product.descr
            'price': 1337,  # product.price
        }
    )
    # except:
    #   pass

    resp = {
        'result': 'success',
        'type': 'wishlist',
        'data': resp
    }
    
    return web.json_response(resp)


@auth_mw
async def add_to_wishlist(request: web.Request, context):
    uid = request.cookies['id']
    pid = request.query.get('query')
    # data = await ORM.add_product(uid, pid)
    # if data is None:
    #   resp = ['failure']
    # else:
    #   resp = ['success']

    resp = {
        'result': 'success',
        'type': 'wishlist_add'
    }
    
    return web.json_response(resp)


@auth_mw
async def delete_from_wishlist(request: web.Request, context):
    uid = request.cookies['id']
    pid = request.query.get('query')
    # data = await ORM.delete_product(uid, pid)
    # if data is None:
    #   resp = ['failure']
    # else:
    #   resp = ['success']

    resp = {
        'result': 'success',
        'type': 'wishlist_remove'
    }
    
    return web.json_response(resp)


@auth_mw
async def get_user_wishlist(request: web.Request, context):
    resp = list()
    uid = request.query.get('query')
    # try:
    #   data = await ORM.get_user_gifts(uid)
    #   for _ in data:
    #       resp.append(_)
    resp.append(
        {
            'ref': 'url',  # product.ref
            'img': 'img_url',  # product.img
            'name': 'name',  # product.name
            'type': 'type',  # product.type
            'descr': 'description',  # product.descr
            'price': 1337,  # product.price
        }
    )
    # except:
    #   resp.append('no gifts reserved')

    resp = {
        'result': 'success',
        'type': 'user_wishlist',
        'data': resp
    }
    
    return web.json_response(resp)


@auth_mw
async def reserve_gift_for_user(request: web.Request, context):
    uid = request.query.get('query')
    # data = await ORM.add_gift(uid, pid)
    # if data is None:
    #   resp = ['failure']
    # else:
    #   resp = ['success']

    resp = {
        'result': 'success',
        'type': 'user_gift_add'
    }
    
    return web.json_response(resp)


@auth_mw
async def cancel_gift_for_user(request: web.Request, context):
    uid = request.query.get('query')
    # data = await ORM.delete_gift(uid, pid)
    # if data is None:
    #   resp = ['failure']
    # else:
    #   resp = ['success']

    resp = {
        'result': 'success',
        'type': 'user_gift_remove'
    }
    
    return web.json_response(resp)


async def login(request: web.Request):
    # The needed info is already obtained from frontend request
    # All we need is to check sign validity
    vksign = request.query.get("sign")
    if vksign is None:
        return unauthorized_response()

    vkquery = request.query
    if not vk_validation(query=vkquery, secret=app_secret):
        return unauthorized_response()

    try:
        uid = await add_user(request)
    except ErrorUnauthorized:
        return unauthorized_response()

    jwt_token = await request.app.auth_connection.call(uid)
    resp = {
        'result': 'success',
        'type': 'login'
    }

    response = web.json_response(resp)
    response.set_cookie(name="jwt_token", value=jwt_token)
    return response
