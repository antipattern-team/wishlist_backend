from orm.orm import *


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
    gid = IntField(required=False)

    class Meta:
        table_name = 'wants'


class Friend(Model):
    id = IntPrimaryField()
    uid = IntField()
    fid = IntField()

    class Meta:
        table_name = 'friends'


class Popular(Model):
    pid = IntPrimaryField()
    rate = IntField(required=False)

    class Meta:
        table_name = 'popular'