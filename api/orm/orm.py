import asyncio
import asyncpg

# todo
# 1) Unique fields
# 2) Orderby
# 3) Filter > < >= <= conditionals


class _QueryVariableGenerator:
    def __init__(self):
        self._counter = 1
        self._variables = []

    def get_variable(self, variable):
        if isinstance(variable, int):
            query = f'${self._counter}::integer'
        elif isinstance(variable, bool):
            query = f'${self._counter}::bool'
        else:
            query = f'${self._counter}'

        self._counter += 1
        self._variables.append(variable)

        return query

    @property
    def variables(self):
        return self._variables


class Field:
    def __init__(self, f_type, required=True, default=None):
        self.f_type = f_type
        self.required = required
        self.default = default

    def validate(self, value):
        if value is None:
            if self.required:
                if self.default:
                    # return self.f_type(self.default)
                    return self.default
                else:
                    raise ValueError('missing value for required field')
            else:
                return None

        return self.f_type(value)


class IntField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(int, required, default)


class StringField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(str, required, default)


class BoolField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(bool, required, default)


class Primary:
    pass


class IntPrimaryField(Primary, IntField):
    pass


class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        meta = namespace.get('Meta')
        if meta is None:
            raise ValueError('meta is none')
        if not hasattr(meta, 'table_name'):
            raise ValueError('table_name is empty')

        namespace['_table_name'] = meta.table_name

        class DoesNotExist(Exception):
            def __init__(self, *args, **kwargs):
                super().__init__(self, *args, **kwargs)

        namespace['DoesNotExist'] = DoesNotExist

        fields = {k: v for k, v in namespace.items()
                  if isinstance(v, Field)}

        for cls in bases:
            if cls is Model:
                continue
            fields = {**fields, **cls.__dict__['_fields']}

        primary_found = False
        for name, field in fields.items():
            if isinstance(field, Primary):
                if primary_found:
                    raise ValueError(f'Second primary key encountered: {name}')
                else:
                    primary_found = True
                    namespace['_primary'] = name

        if not primary_found:
            raise ValueError('No primary key found')

        namespace['_fields'] = fields

        return super().__new__(mcs, name, bases, namespace)


class QuerySet:
    def __init__(self, _connection, _model, **kwargs):
        self._model = _model
        self._filter = {}
        self._slices = []
        self._conn = _connection

        self._add_rules(**kwargs)

    def _add_rules(self, **kwargs):
        # print('[_add_rules]', kwargs)
        for k, v in kwargs.items():
            if k not in self._model._fields:
                raise ValueError(f'Unknown field {k}')
            self._filter[k] = self._model._fields[k].validate(v)

        # self._filter = {**self._filter, **kwargs}

    def filter(self, **kwargs):
        self._add_rules(**kwargs)
        # print(self._filter)
        return self

    def __getitem__(self, item):
        if not isinstance(item, slice):
            raise ValueError('Slice should be passed')
        self._slices.append(item)
        return self

    async def get(self):
        query = f'SELECT * FROM {self._model._table_name}'

        gen = _QueryVariableGenerator()

        if len(self._filter):
            query = f'SELECT * FROM {self._model._table_name} WHERE    '

            for k, v in self._filter.items():
                query += f' {k} = {gen.get_variable(v)} and'
            query = query[:-4]

        if self._slices:
            offset = 0
            stop = None
            limit = None

            for s in self._slices:
                if (s.start and s.start < 0) or (s.stop and s.stop < 0):
                    raise ValueError('Slice\'s start and stop should be > 0 or None')
                if s.step and s.step != 1:
                    raise ValueError('Slice\'s step should be None or 1')
                if s.stop and s.start and s.stop < s.start:
                    raise ValueError('Stop can\'t be < than start')

                offset += s.start or 0

                if s.stop is None:
                    continue

                if stop is None:
                    stop = s.stop
                else:
                    if offset + s.stop > stop:
                        raise ValueError('Can\'t filter more than you had on the previous filter step')
                    stop = offset + s.stop

                limit = stop - offset

            if offset:
                query += f' OFFSET {offset}'

            if limit:
                query += f' LIMIT {limit}'

        query += ';'
        # print(query)

        models = []
        objects = await self._conn.fetch(query, *gen.variables)
        for obj in objects:
            fields = {}
            for field in self._model._fields:
                fields[field] = obj[field]
            models.append(self._model(**fields))

        if len(models) == 0:
            raise self._model.DoesNotExist

        return models

    async def __aiter__(self):
        models = await self.get()
        for model in models:
            yield model

    async def update(self, **kwargs):
        query = f'UPDATE {self._model._table_name} SET '

        gen = _QueryVariableGenerator()

        for k, v in kwargs.items():
            if k not in self._model._fields:
                raise ValueError(f'Unknown field {k}')

            v = self._model._fields[k].validate(v)

            query += f' {k} = {gen.get_variable(v)},'

        query = query[:-1]

        if len(self._filter) > 0:
            query += ' WHERE'
            for k, v in self._filter.items():
                v = self._model._fields[k].validate(v)

                query += f' {k} = {gen.get_variable(v)} and'
            query = query[:-4]

        query += ';'

        # print(query)
        await self._conn.execute(query, *gen.variables)

    async def delete(self):
        query = f'DELETE FROM {self._model._table_name} WHERE    '

        gen = _QueryVariableGenerator()

        for k, v in self._filter.items():
            query += f' {k} = {gen.get_variable(v)} and'
        query = query[:-4] + ';'

        # print(query)
        await self._conn.execute(query, *gen.variables)


class Manage:
    _conn = None

    @classmethod
    async def init_conn(cls, user, password, database, host):
        cls._conn = await asyncpg.connect(user=user, password=password,
                                          database=database, host=host)

    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        if self.model_cls is None:
            self.model_cls = owner
        return self

    async def create(self, **kwargs):
        await self.model_cls(**kwargs).save()

    async def update(self, **kwargs):
        return await QuerySet(self._conn, self.model_cls).update(**kwargs)

    async def delete(self, **kwargs):
        return await QuerySet(self._conn, self.model_cls).delete(**kwargs)

    async def get(self):
        return await QuerySet(self._conn, self.model_cls).get()

    def filter(self, **kwargs):
        return QuerySet(self._conn, self.model_cls, **kwargs)


class Model(metaclass=ModelMeta):
    class Meta:
        table_name = ''

    objects = Manage()

    def __init__(self, *_, **kwargs):
        self.__dict__['_is_valid'] = True

        for field_name, field in self._fields.items():
            setattr(self, field_name, kwargs.get(field_name))

    def __setattr__(self, name, value):
        if name in self._fields:
            field = self._fields[name]
            curr_value = getattr(self, name)
            if isinstance(field, Primary) and curr_value is not None and not isinstance(curr_value, Field):
                raise ValueError('Primary key can\'t be reassigned')

            value = field.validate(value)
            self.__dict__[name] = value

    def _invalidate(self):
        for key in self.__dict__:
            self.__dict__[key] = None

        self.__dict__['_is_valid'] = False

    def is_valid(self) -> bool:
        return self._is_valid

    def __bool__(self):
        return self.is_valid()

    async def save(self):
        primary_field = self._primary

        none_fields = []

        if getattr(self, primary_field) is not None:
            query = f'INSERT INTO {self._table_name}('
            for k in self._fields:
                if getattr(self, k) is None:
                    none_fields.append(k)
                    continue
                query += f'{k},'
            query = query[:-1] + ') '

            gen = _QueryVariableGenerator()

            query += 'VALUES('
            for k in self._fields:
                if getattr(self, k) is None:
                    continue
                v = getattr(self, k)
                query += f'{gen.get_variable(v)},'
            query = query[:-1] + f')'

            query += f' ON CONFLICT({primary_field}) DO UPDATE SET'
            for k in self._fields:
                if k == primary_field:
                    continue

                v = getattr(self, k)
                if v is None:
                    continue

                query += f' {k} = {gen.get_variable(v)},'
            # query = query[:-1] + f' WHERE {primary_field} = {getattr(self, primary_field)}  '
            query = query[:-1]

            if len(none_fields) > 0:
                query += ' RETURNING '
                for field in none_fields:
                    query += f'{field}, '
                query = query[:-2]

            query += ';'
        else:
            query = f'INSERT INTO {self._table_name}('

            gen = _QueryVariableGenerator()

            for k in self._fields:
                if k == primary_field or getattr(self, k) is None:
                    none_fields.append(k)
                    continue
                query += f'{k},'
            query = query[:-1] + ') '

            query += 'VALUES('
            for k in self._fields:
                if k == primary_field or getattr(self, k) is None:
                    continue
                v = getattr(self, k)
                query += f'{gen.get_variable(v)},'
            query = query[:-1] + ') RETURNING '

            for field in none_fields:
                query += f'{field}, '
            query = query[:-2] + ';'

        # print(query)

        if len(none_fields) > 0:
            res = (await self.objects._conn.fetch(query, *gen.variables))[0]
            for field in none_fields:
                setattr(self, field, res[field])
        else:
            await self.objects._conn.execute(query, *gen.variables)

    async def delete(self):
        primary_field = self._primary

        value = getattr(self, primary_field)
        if value is None:
            raise ValueError('Can\'t delete what\'s not saved')

        await self.objects.filter(**{primary_field: value}).delete()
        self._invalidate()


async def _orm_test():
    await Manage.init_conn(user='postgres', password='', database='test', host='localhost')

    class User(Model):
        uid = IntPrimaryField(required=False)
        vkid = StringField()
        wishes = BoolField(required=False)

        class Meta:
            table_name = 'users'

    #
    #
    # class Man(User):
    #     sex = StringField()
    #
    #     class Meta:
    #         table_name = 'man'
    #
    #
    # class ManOfCulture(Man):
    #     culture = IntField()
    #
    #     class Meta:
    #         table_name = 'man_of_culture'
    #
    # user = User(uid=1, vkid='name', wishes=True)
    # print(user.__dict__)
    #
    # man = Man(uid=1, vkid='name', sex='best', wishes=True)
    # print(man.__dict__)
    #
    # man_of_culture = ManOfCulture(uid=1, vkid='name', sex='best', culture=100, wishes=True)
    # print(man_of_culture.__dict__)
    # print(ManOfCulture._table_name)
    #
    # try:
    #     user.id = 'qwe'
    # except ValueError:
    #     print("ValueError as expected")
    #
    # try:
    #     user.name = 123
    #     print("NO ValueError as expected")
    # except ValueError:
    #     pass
    #
    # print(user.__dict__)

    saved_user = User(vkid='DIO')
    print('[main]: DICT', saved_user.__dict__)
    try:
        await saved_user.save()
    except asyncpg.exceptions.UniqueViolationError as e:
        print('EXPECTED exception:', e.args)
    print(saved_user.uid)
    print('[main]: DICT', saved_user.__dict__)

    print()

    saved_user = User(uid=23, vkid='try qqit')
    print('[main]: DICT', saved_user.__dict__)
    await saved_user.save()
    print('[main]: DICT', saved_user.__dict__)

    print()

    print('[main] is_valid:', saved_user.is_valid())
    await saved_user.delete()
    print('[main]: DICT', saved_user.__dict__)
    print('[main] is_valid:', saved_user.is_valid())

    #
    # try:
    #     raise User.DoesNotExist('lol')
    # except Man.DoesNotExist:
    #     print('UNEXPECTED Man.DoesNotExist')
    # except User.DoesNotExist:
    #     print('User.DoesNotExist as expected')
    #
    #
    # data = await User.objects.filter(uid=2).filter(vkid='petya')[:19].get()
    # for obj in data:
    #     print(obj)
    #
    # data = await User.objects.get()
    # for obj in data:
    #     try:
    #         print(obj.uid, obj.vkid, obj.wishes)
    #         obj.uid = 10
    #     except ValueError as v:
    #         print('Got error:', v.args)
    #
    async for obj in User.objects.filter():
        print(obj.uid, obj.vkid, obj.wishes)

    # User.objects.create(id=1, name='name')
    # User.objects.update(id=1)
    # User.objects.delete(id=1)
    #

    # user.name = '2'
    # user.save()
    # user.delete()


if __name__ == '__main__':
    asyncio.run(_orm_test())
