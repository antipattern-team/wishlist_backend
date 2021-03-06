from aiohttp import web
from middleware import auth_mw
from models import *


# todo elastic
async def get_products_search(request):
    resp = list()
    product_name = request.match_info['name']

    resp.append(
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


async def get_products_popular(request):
    resp = list()

    try:
        popular = await Popular.objects.get()
    except Popular.DoesNotExist:
        popular = []

    sorted(popular, key=lambda p: p.rate, reverse=True)

    for pop in popular:
        product = await Product.objects.filter(pid=pop.pid).get_one()
        resp.append({
                'pid': product.pid,
                'reference': product.reference,
                'image': product.image,
                'name': product.name,
                'product_type': product.product_type,
                'description': product.description,
                'price': product.price
            })

    resp = {
        'result': 'success',
        'type': 'popular',
        'data': resp
    }

    return web.json_response(resp)


@auth_mw
async def get_friends(request, context):
    resp = list()
    uid = context['uid']

    for friend_id in await Friend.objects.filter(uid=uid):
        user = await User.objects.filter(uid=friend_id).get_one()
        if user.wishes > 0:  # todo remove this when proper conditions implemented
            resp.append({
                'vkid': user.vkid
            })

    resp = {
        'result': 'success',
        'type': 'friends',
        'data': resp
    }
    
    return web.json_response(resp)

# todo elastic
@auth_mw
async def get_friends_search(request, context):
    resp = list()
    friend_name = request.match_info['name']
    uid = context['uid']

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
async def get_gifts(request, context):
    resp = list()
    uid = context['uid']

    try:
        gifts = await Wants.objects.filter(gid=uid)
    except Wants.DoesNotExist:
        gifts = []

    for gift in gifts:
        user = await User.objects.filter(uid=gift.uid).get_one()
        product = await Products.objects.filter(pid=gift.pid).get_one()

        resp.append({
            'user': {
                'vkid': user.vkid
            },
            'product': {
                'pid': product.pid,
                'reference': product.reference,
                'image': product.image,
                'name': product.name,
                'product_type': product.product_type,
                'description': product.description,
                'price': product.price
            }
        })

    resp = {
        'result': 'success',
        'type': 'gifts',
        'data': resp
    }
    
    return web.json_response(resp)


@auth_mw
async def get_wishlist(request, context):
    resp = list()
    uid = context['uid']

    try:
        wishes = await Wants.objects.filter(uid=uid)
    except Wants.DoesNotExist:
        wishes = []

    for wish in wishes:
        if wish.gid is None:
            reserved = False
        else:
            reserved = True

        product = await Product.objects.filter(pid=wish.pid).get_one()

        resp.append({
            'product': {
                'pid': product.pid,
                'reference': product.reference,
                'image': product.image,
                'name': product.name,
                'product_type': product.product_type,
                'description': product.description,
                'price': product.price
            },
            'reserved': reserved
        })

    resp = {
        'result': 'success',
        'type': 'wishlist',
        'data': resp
    }
    
    return web.json_response(resp)


@auth_mw
async def add_to_wishlist(request, context):
    uid = context['uid']

    try:
        body = await request.json()
    except:
        body = {
            'result': 'fail',
            'type': 'wishlist_add',
            'source': 'body',
            'info': 'Request body is empty'
        }
        return web.json_response(body, status=400)

    try:
        pid = body['pid']
    except:
        body = {
            'result': 'fail',
            'type': 'wishlist_add',
            'source': 'pid',
            'info': 'pid is not specified in request body'
        }
        return web.json_response(body, status=400)

    try:
        await Product.objects.filter(pid=pid)
    except Product.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'wishlist_add',
            'source': 'pid',
            'info': 'Can\'t find product with such pid'
        }
        return web.json_response(body, status=404)

    try:
        await Wants.objects.create(uid=uid, pid=pid)
    except Wants.UniqueViolation:
        body = {
            'result': 'fail',
            'type': 'wishlist_add',
            'source': 'vkid and pid',
            'info': 'This product is already added to the wishlist'
        }
        return web.json_response(body, status=409)

    resp = {
        'result': 'success',
        'type': 'wishlist_add'
    }
    
    return web.json_response(resp)


@auth_mw
async def delete_from_wishlist(request, context):
    uid = context['uid']

    try:
        body = await request.json()
    except:
        body = {
            'result': 'fail',
            'type': 'wishlist_remove',
            'source': 'body',
            'info': 'Request body is empty'
        }
        return web.json_response(body, status=400)

    try:
        pid = body['pid']
    except:
        body = {
            'result': 'fail',
            'type': 'wishlist_remove',
            'source': 'pid',
            'info': 'pid is not specified in request body'
        }
        return web.json_response(body, status=400)

    try:
        product = await Product.objects.filter(pid=pid)
    except Product.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'wishlist_remove',
            'source': 'pid',
            'info': 'Can\'t find product with such pid'
        }
        return web.json_response(body, status=404)



    deleted_objects = await Wants.objects.delete(uid=uid, pid=product.pid)
    if len(deleted_objects) == 0:
        body = {
            'result': 'fail',
            'type': 'wishlist_remove',
            'source': 'vkid and pid',
            'info': 'This product isn\'t added to the wishlist'
        }
        return web.json_response(body, status=409)

    resp = {
        'result': 'success',
        'type': 'wishlist_remove'
    }
    
    return web.json_response(resp)


async def get_user_wishlist(request):
    resp = list()
    vkid = request.match_info['vkid']

    try:
        user = await User.objects.filter(vkid=vkid).get_one()
    except User.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'user_wishlist',
            'source': 'vkid',
            'info': 'User with such vkid does not exist'
        }
        return web.json_response(body, status=404)
    try:
        wishes = await Wants.objects.filter(uid=user.uid)
    except Wants.DoesNotExist:
        wishes = []

    for wish in wishes:
        if wish.gid is None:
            reserved = False
        else:
            reserved = True

        product = await Product.objects.filter(pid=wish.pid).get_one()

        resp.append({
            'product': {
                'pid': product.pid,
                'reference': product.reference,
                'image': product.image,
                'name': product.name,
                'product_type': product.product_type,
                'description': product.description,
                'price': product.price
            },
            'reserved': reserved
        })

    resp = {
        'result': 'success',
        'type': 'user_wishlist',
        'data': resp
    }

    return web.json_response(resp)


@auth_mw
async def reserve_gift_for_user(request, context):
    gid = context['uid']
    vkid = request.match_info['vkid']

    try:
        body = await request.json()
    except:
        body = {
            'result': 'fail',
            'type': 'user_gift_add',
            'source': 'body',
            'info': 'Request body is empty'
        }
        return web.json_response(body, status=400)

    try:
        pid = body['pid']
    except:
        body = {
            'result': 'fail',
            'type': 'user_gift_add',
            'source': 'pid',
            'info': 'pid is not specified in request body'
        }
        return web.json_response(body, status=400)

    try:
        user = await User.objects.filter(vkid=vkid).get_one()
    except User.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'user_gift_add',
            'source': 'vkid',
            'info': 'User with such vkid does not exist'
        }
        return web.json_response(body, status=404)

    try:
        await Product.objects.filter(pid=pid)
    except Product.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'user_gift_add',
            'source': 'pid',
            'info': 'Can\'t find product with such pid'
        }
        return web.json_response(body, status=404)

    try:
        wants = await Wants.objects.filter(uid=user.uid, pid=pid)
    except Wants.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'user_gift_add',
            'source': 'vkid and pid',
            'info': 'Can\'t find such gift'
        }
        return web.json_response(body, status=404)

    if wants.gid is not None:
        body = {
            'result': 'fail',
            'type': 'user_gift_add',
            'source': 'vkid and pid',
            'info': 'This gift is already reserved'
        }
        return web.json_response(body, status=409)

    wants.gid = gid
    await wants.save()

    resp = {
        'result': 'success',
        'type': 'user_gift_add'
    }

    return web.json_response(resp)


@auth_mw
async def cancel_gift_for_user(request, context):
    gid = context['uid']
    vkid = request.match_info['vkid']

    try:
        body = await request.json()
    except:
        body = {
            'result': 'fail',
            'type': 'user_gift_remove',
            'source': 'body',
            'info': 'Request body is empty'
        }
        return web.json_response(body, status=400)

    try:
        pid = body['pid']
    except:
        body = {
            'result': 'fail',
            'type': 'user_gift_remove',
            'source': 'pid',
            'info': 'pid is not specified in request body'
        }
        return web.json_response(body, status=400)

    try:
        user = await User.objects.filter(vkid=vkid).get_one()
    except User.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'user_gift_remove',
            'source': 'vkid',
            'info': 'User with such vkid does not exist'
        }
        return web.json_response(body, status=404)

    try:
        await Product.objects.filter(pid=pid)
    except Product.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'user_gift_remove',
            'source': 'pid',
            'info': 'Can\'t find product with such pid'
        }
        return web.json_response(body, status=404)

    try:
        wants = await Wants.objects.filter(uid=user.uid, pid=pid)
    except Wants.DoesNotExist:
        body = {
            'result': 'fail',
            'type': 'user_gift_remove',
            'source': 'vkid and pid',
            'info': 'Can\'t find such gift'
        }
        return web.json_response(body, status=404)

    if wants.gid != gid:
        body = {
            'result': 'fail',
            'type': 'user_gift_remove',
            'source': 'vkid and pid',
            'info': 'This gift isn\'t reserved by current user'
        }
        return web.json_response(body, status=409)

    wants.gid = None
    await wants.save()

    resp = {
        'result': 'success',
        'type': 'user_gift_remove'
    }
    
    return web.json_response(resp)
