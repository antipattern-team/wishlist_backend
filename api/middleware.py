from aiohttp import web
from models import *
import jwt
from settings import auth_key

# todo(Usatiynyan):
#  edge cases \?


def auth_mw(handler):
    async def func(request: web.Request):
        jwt_present = "jwt_token" in request.cookies.keys()
        # 0) check if jwt_token is_valid
        if jwt_present:
            jwt_token = request.cookies.get("jwt_token")
            try:
                decoded_token = jwt.decode(jwt_token, auth_key, algorithms='HS256')
            except jwt.exceptions.PyJWTError:
                jwt_present = False
                # 0.5) if not valid, just delete it => rewrite the cookie
                pass

        if jwt_present:
            uid = decoded_token.get("uid")
        else:
            # id from request
            # variant 1) The needed id is already obtained from frontend request
            # variant 2) Insert vk api request for user data here
            # todo(Usatiynyan): remake when vktoken implemented
            vkid = request.query.get("vktoken")
            if vkid is None:
                unaouthrized_response = web.Response()
                unaouthrized_response.set_status(status=403)
                return unaouthrized_response

            uid = await add_user(vkid)

            jwt_token = await request.app.auth_connection.call(uid)

        context = {'uid': uid}
        response: web.Response = await handler(request, context)

        if not jwt_present:
            response.set_cookie(name="jwt_token", value=jwt_token)

        return response

    return func


async def add_user(vkid):
    try:
        user = (await User.objects.filter(vkid=vkid).get())[0]
    except User.DoesNotExist:
        user = User(vkid=vkid)
        await user.save()

    # Insert another vk api request for user's friends here
    friend_vk_ids = []
    for friend_id in friend_vk_ids:
        try:
            friend = (await User.objects.filter(vkid=friend_id).get())[0]
        except User.DoesNotExist:
            continue

        await Friend.objects.create(uid=user.uid, fid=friend.uid)
        await Friend.objects.create(uid=friend.uid, fid=user.uid)

    return user.uid
