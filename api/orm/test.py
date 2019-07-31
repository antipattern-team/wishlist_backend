import asyncio
from orm import *


class User(Model):
    uid = IntPrimaryField()
    vkid = StringField()
    wishes = IntField(required=True, default=0)

    class Meta:
        table_name = 'users'


class Product(Model):
    pid = IntPrimaryField()
    reference = StringField()
    image = StringField()
    name = StringField()
    product_type = StringField(required=False)
    description = StringField(required=False)
    price = IntField()

    class Meta:
        table_name = 'products'


class Wants(Model):
    id = IntPrimaryField()
    uid = IntField()
    pid = IntField()
    gid = IntField(required=False, default=None)

    class Meta:
        table_name = 'wants'


async def test():
    await Manage.init_conn(user='postgres', password='', database='wishlist', host='localhost')
    # # реализовать create, filter, update, delete через objects
    # await User.objects.create(id=1, name='name')
    # await User.objects.update(name='name')
    # await User.objects.filter(name='name').delete()
    # # поддержать ленивое выполнение запроса
    # queryset = User.objects.filter(var1='1')
    # # поддержать limit, offset через slice
    # queryset = queryset.filter(var2='2')[:5]
    #
    # try:
    #     async for _ in queryset:
    #         pass
    #     raise AssertionError
    # except User.DoesNotExist:
    #     pass
    #
    # # реализовать save, update (save), delete через модель
    # user = User(id=1, name='name')
    # await user.save()
    # assert (await User.objects.get())[0].name == 'name'
    # user.name = '2'
    # await user.save()
    # assert (await User.objects.get())[0].name == '2'
    # await user.delete()
    #
    # # реализовать метод get, который кидает exception,
    # # специфичный для конкретной модели (User.DoesNotExist)
    # try:
    #     await User.objects.get()
    #     raise AssertionError
    # except User.DoesNotExist:
    #     pass

    user = User(vkid='test1')
    await user.save()
    try:
        user1 = User(vkid='test1')
        await user1.save()
    except User.UniqueViolation:
        print('UniqueViolation')
    print(user.__dict__)

    product = Product(reference='ref', image='img', name='name', price=100)
    await product.save()
    print(product.__dict__)

    wants = Wants(uid=user.uid, pid=product.pid)
    await wants.save()

    print(wants.__dict__)

    wants.gid = user.uid
    await wants.save()
    wants.gid = None
    await wants.save()

    print(wants.__dict__)

    print('delete wants')
    await wants.delete()
    print('delete product')
    await product.delete()
    print('delete user')
    user_deleted = User(uid=user.uid, vkid=user.vkid)

    updated_objects = await User.objects.filter(uid=user.uid).update(wishes=1)
    if len(updated_objects) != 1:
        raise AssertionError

    deleted_objects = await user.delete()
    if len(deleted_objects) != 1:
        raise AssertionError

    deleted_objects = await user_deleted.delete()
    if len(deleted_objects) != 0:
        raise AssertionError

    updated_objects = await User.objects.update(wishes=1)
    if len(updated_objects) != 0:
        raise AssertionError

if __name__ == '__main__':
    asyncio.run(test())
