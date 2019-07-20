from aiohttp import web
from middleware import auth_mw


async def get_products_popular(request):
    resp = list()
    # try:
    #   data = await ORM.get_all_products()
    #   for _ in data:
    #       resp.append(_)
    # except:
    #   pass
    resp.append(  # todo(UsatiyNyan): modify when ORM is ready
        {
            "ref": "url",  # data[i].ref
            "img": "img_url",  # data[i].img
            "name": "name",  # data[i].name
            "type": "type",  # data[i].type
            "descr": "description",  # data[i].descr
            "price": 1337,  # data[i].price
        }
    )
    return web.json_response(resp)


@auth_mw
async def get_friends(request):
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
            "friend_img": "some_url",  # data[i].img
            "friend_name": "anonymous",  # data[i].name
        }
    )
    return web.json_response(resp)


@auth_mw
async def get_friends_search(request):
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
    #   resp.append("you have no friends")
    resp.append(
        {
            "friend_img": "some_url",  # data[i].img
            "friend_name": "anonymous",  # data[i].name
        }
    )
    return web.json_response(resp)


@auth_mw
async def get_gifts(request):
    resp = list()
    gid = request.cookies.get('id')
    # try:
    #   data = await ORM.get_gifts(gid)
    #   for _ in data:
    #       resp.append(_)
    # except:
    #   resp.append("no gifts reserved")
    resp.append(  # todo(UsatiyNyan): consult with Max about API's response
        {
            "friend_img": "some_url",  # data.users[i].img
            "friend_name": "anonymous",  # data.users[i].name
            "gifts": [
                {
                    "gift_info": "some_info"  # data.users.gift_info
                }
            ]
        }
    )
    return web.json_response(resp)


@auth_mw
async def get_wishlist(request):
    resp = list()
    uid = request.cookies.get('id')
    keyword = request.query.get('query')  # "reserved=-1", "unreserved=1", "all=0"
    # try
    # if keyword is reserved: data = await ORM.get_wishlist(uid).filter('gid', None, ops.ne)
    # if keyword is unreserved: data = await ORM.get_wishlist(uid).filter('gid', None, ops.eq)
    # if keyword is all: data = await ORM.get_wishlist(uid).get('gid')
    resp.append(
        {
            "ref": "url",  # product.ref
            "img": "img_url",  # product.img
            "name": "name",  # product.name
            "type": "type",  # product.type
            "descr": "description",  # product.descr
            "price": 1337,  # product.price
        }
    )
    # except:
    #   pass
    return web.json_response(resp)


@auth_mw
async def post_wishlist(request):
    uid = request.cookies['id']
    pid = request.query.get('query')
    # data = await ORM.add_product(uid, pid)
    # if data is None:
    #   resp = ["failure"]
    # else:
    #   resp = ["success"]
    resp = ["success"]
    return web.json_response(resp)


@auth_mw
async def delete_wishlist(request):
    uid = request.cookies['id']
    pid = request.query.get('query')
    # data = await ORM.delete_product(uid, pid)
    # if data is None:
    #   resp = ["failure"]
    # else:
    #   resp = ["success"]
    resp = ["success"]
    return web.json_response(resp)


@auth_mw
async def get_user(request):
    resp = list()
    uid = request.query.get('query')
    # try:
    #   data = await ORM.get_user_gifts(uid)
    #   for _ in data:
    #       resp.append(_)
    resp.append(
        {
            "ref": "url",  # product.ref
            "img": "img_url",  # product.img
            "name": "name",  # product.name
            "type": "type",  # product.type
            "descr": "description",  # product.descr
            "price": 1337,  # product.price
        }
    )
    # except:
    #   resp.append("no gifts reserved")
    return web.json_response(resp)


@auth_mw
async def post_user(request):
    uid = request.query.get('query')
    # data = await ORM.add_gift(uid, pid)
    # if data is None:
    #   resp = ["failure"]
    # else:
    #   resp = ["success"]
    resp = ["success"]
    return web.json_response(resp)


@auth_mw
async def delete_user(request):
    uid = request.query.get('query')
    # data = await ORM.delete_gift(uid, pid)
    # if data is None:
    #   resp = ["failure"]
    # else:
    #   resp = ["success"]
    resp = ["success"]
    return web.json_response(resp)
