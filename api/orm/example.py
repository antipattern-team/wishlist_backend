import asyncio
from orm import *


class User(Model):
    uid = IntPrimaryField(required=False)
    vkid = StringField()
    wishes = IntField(required=False, default=0)

    class Meta:
        table_name = 'users'


class Friend(Model):
    id = IntPrimaryField(required=False)
    uid = IntField()
    fid = IntField()

    class Meta:
        table_name = 'friends'


async def test():
    await Manage.init_conn(user='postgres', password='', database='test', host='localhost')

    # 0) JWT check
    # 0.5) if not valid, just delete it
    jwt_present = False

    # 1) The needed id is already obtained from frontend request
    # 2) Insert vk api request for user data here

    if not jwt_present:
        # id from request
        id = 'blabla'

        try:
            user = (await User.objects.filter(vkid=id).get())[0]
        except User.DoesNotExist:
            user = User(vkid=id)
            user.save()

        # Insert another vk api request for user's friends here

        friend_vk_ids = []
        for friend_id in friend_vk_ids:
            try:
                friend = (await User.objects.filter(vkid=friend_id).get())[0]
            except User.DoesNotExist:
                return None

            await Friend.objects.create(uid=user.uid, fid=friend.uid)
            await Friend.objects.create(uid=friend.uid, fid=user.uid)

        uid = user.uid
    else:
        # obtain uid from jwt
        uid = 1

    # last) Renew jwt

    return uid


if __name__ == '__main__':
    asyncio.run(test())
