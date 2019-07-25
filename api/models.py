from orm.orm import *


class User(Model):
    uid = IntPrimaryField(required=False)
    vkid = StringField()
    wishes = IntField(required=False, default=0)

    class Meta:
        table_name = 'users'


class Product(Model):
    pid = IntPrimaryField(required=False)
    ref = StringField()
    img = StringField()
    name = StringField()
    ptype = StringField(required=False)
    descr = StringField(required=False)
    price = IntField()

    class Meta:
        table_name = 'products'


class Wants(Model):
    id = IntPrimaryField(required=False)
    uid = IntField()
    pid = IntField()
    gid = IntField(required=False, default=None)

    class Meta:
        table_name = 'wants'


class Friend(Model):
    id = IntPrimaryField(required=False)
    uid = IntField()
    fid = IntField()

    class Meta:
        table_name = 'friends'


class Popular(Model):
    pid = IntPrimaryField(required=False)
    rate = IntField(required=False)

    class Meta:
        table_name = 'popular'
