from aiohttp import web
from models import *
import jwt
from settings import auth_key
import requests

# todo(Usatiynyan):
#  edge case error 6 and error !6
#  only 5 requests per second!


def auth_mw(handler):
    async def func(request: web.Request):
        jwt_present = "jwt_token" in request.cookies.keys()
        # 0) check if jwt_token is_valid
        if jwt_present:
            jwt_token = request.cookies.get("jwt_token")
            try:
                decoded_token = jwt.decode(jwt_token, auth_key, algorithms=['HS256'])
            except jwt.exceptions.PyJWTError:
                jwt_present = False
                # 0.5) if not valid, just delete it => rewrite the cookie
                pass

        if jwt_present:
            uid = decoded_token.get("uid")
        else:
            # The needed token is already obtained from frontend request
            vktoken = request.query.get("vktoken")
            if vktoken is None:
                return unauthorized_response()

            uid = await add_user(vktoken)

            jwt_token = await request.app.auth_connection.call(uid)

        context = {'uid': uid}
        response: web.Response = await handler(request, context)

        if not jwt_present:
            response.set_cookie(name="jwt_token", value=jwt_token)

        return response

    return func


async def add_user(vktoken):
    user_response = requests.get('https://api.vk.com/method/users.get',
                                 params={
                                     'fields': 'photo_200_orig',
                                     'v': '5.101',
                                     'access_token': vktoken}).json()

    try:
        vkid = user_response['response'][0]['id']
    except (TypeError, KeyError):
        return unauthorized_response()

    try:
        user = (await User.objects.filter(vkid=vkid).get())[0]
    except User.DoesNotExist:
        user = User(vkid=vkid)
        await user.save()

    friends_response = requests.get('https://api.vk.com/method/friends.get',
                                    params={
                                        'fields': 'photo_200_orig',
                                        'v': '5.101',
                                        'access_token': vktoken}).json()

    try:
        friends_vk = friends_response['response']['items']
    except (TypeError, KeyError):  # what if you have no friends?
        return unauthorized_response()

    for friend_vk in friends_vk:
        try:
            friend_id = friend_vk.get('id')
            if friend_id is None:
                continue
            friend = (await User.objects.filter(vkid=friend_id).get())[0]
        except User.DoesNotExist:
            continue

        await Friend.objects.create(uid=user.uid, fid=friend.uid)
        await Friend.objects.create(uid=friend.uid, fid=user.uid)

    return user.uid


def unauthorized_response():
    resp = web.Response()
    resp.set_status(status=401)
    return resp
