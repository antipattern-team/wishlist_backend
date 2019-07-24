from api.orm.orm import *


class User(Model):
    uid = IntPrimaryField(required=False)
    vkid = StringField()
    wishes = BoolField(required=False, default=False)

    class Meta:
        table_name = 'users'


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
