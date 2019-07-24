import asyncio
from orm import *

# поддержать 2 типа полей: IntField, StringField.
# Добавить возможность указывать "обязательность поля" (required=False) и значение по умолчанию (default=None)

class User(Model):
    id = IntPrimaryField()
    name = StringField()
    var1 = StringField(required=False, default=None)
    var2 = StringField(required=False, default=None)

    class Meta:
        table_name = 'ormtest'


async def test():
    await Manage.init_conn(user='postgres', password='', database='test', host='localhost')
    # реализовать create, filter, update, delete через objects
    await User.objects.create(id=1, name='name')
    await User.objects.update(name='name')
    await User.objects.filter(name='name').delete()
    # поддержать ленивое выполнение запроса
    queryset = User.objects.filter(var1='1')
    # поддержать limit, offset через slice
    queryset = queryset.filter(var2='2')[:5]

    try:
        async for _ in queryset:
            pass
        raise AssertionError
    except User.DoesNotExist:
        pass

    # реализовать save, update (save), delete через модель
    user = User(id=1, name='name')
    await user.save()
    assert (await User.objects.get())[0].name == 'name'
    user.name = '2'
    await user.save()
    assert (await User.objects.get())[0].name == '2'
    await user.delete()

    # реализовать метод get, который кидает exception,
    # специфичный для конкретной модели (User.DoesNotExist)
    try:
        await User.objects.get()
        raise AssertionError
    except User.DoesNotExist:
        pass


if __name__ == '__main__':
    asyncio.run(test())
