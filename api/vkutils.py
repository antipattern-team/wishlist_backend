from base64 import b64encode
from collections import OrderedDict
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlencode

from aiohttp import web
from models import *


class ErrorUnauthorized(Exception):
    pass


def unauthorized_response():
    return web.json_response(status=401)


def vk_validation(*, query: dict, secret: str) -> bool:
    """Check VK Apps signature"""
    vk_subset = OrderedDict(sorted(x for x in query.items() if x[0][:3] == "vk_"))
    hash_code = b64encode(HMAC(secret.encode(), urlencode(vk_subset, doseq=True).encode(), sha256).digest())
    decoded_hash_code = hash_code.decode('utf-8')[:-1].replace('+', '-').replace('/', '_')
    return query["sign"] == decoded_hash_code


async def add_user(request: web.Request):
    user_info: dict = await request.json()

    try:
        vkid = user_info["user"][0]
    except (TypeError, KeyError):
        raise ErrorUnauthorized

    try:
        user = (await User.objects.filter(vkid=vkid).get())[0]
    except User.DoesNotExist:
        user = User(vkid=vkid)
        await user.save()

    try:
        friends_vk = user_info["friends"]
    except (TypeError, KeyError):
        raise ErrorUnauthorized

    try:
        existing_friends_uid = [f.fid for f in await Friend.objects.filter(uid=user.uid)]
    except Friend.DoesNotExist:
        existing_friends_uid = []

        existing_friends_vk = [(await User.objects.filter(uid=uid).get())[0].vkid for uid in
                               existing_friends_uid]

        existing_friends = dict(zip(existing_friends_vk, existing_friends_uid))

    for existing_friend_vk in existing_friends_vk:
        if existing_friend_vk not in friends_vk:
            # breaking a bond
            await Friend.objects.filter(uid=user.uid, fid=existing_friends[existing_friend_vk]).delete()
            await Friend.objects.filter(uid=existing_friends[existing_friend_vk], fid=user.uid).delete()

    for friend_vk in friends_vk:
        try:
            friend = (await User.objects.filter(vkid=friend_vk).get())[0]
        except User.DoesNotExist:
            continue

        if friend_vk not in existing_friends_vk:
            # creating a bond
            await Friend.objects.create(uid=user.uid, fid=friend.uid)
            await Friend.objects.create(uid=friend.uid, fid=user.uid)

    return user.uid


