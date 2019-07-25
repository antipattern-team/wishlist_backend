from elasticsearch_async import AsyncElasticsearch
import asyncpg


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


class DB:
    async def connect(self, host: str) -> bool:
        pass

    async def drop(self, coll: str) -> None:
        pass

    async def save(self, obj: dict, coll: str, id: int) -> None:
        pass


class ElasticDB(DB):
    def __init__(self):
        self._connection = None

    async def connect(self, host: str) -> bool:
        try:
            self._connection = AsyncElasticsearch(hosts=[host])
        except BaseException:
            return False

        return True

    async def drop(self, coll: str) -> None:
        await self._connection.indices.delete(index=coll, ignore=[400, 404])

    async def save(self, obj: dict, coll: str, id: int) -> None:
        await self._connection.index(index=coll, doc_type='_doc', id=id, body=obj)


class PostgesDB(DB):
    def __init__(self):
        self._pool = None

    async def connect(self, host: str, user: str = '', password: str = '', database: str = '') -> bool:
        try:
            # self._conn = await asyncpg.connect(user=user, password=password,
            #                                    database=database, host=host)
            self._pool = await asyncpg.create_pool(user=user, password=password,
                                                   database=database, host=host)
        except BaseException:
            return False

        return True

    async def drop(self, coll: str) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(f'TRUNCATE TABLE {coll} CASCADE;')

    async def save(self, obj: dict, coll: str, id: int) -> None:
        query = f'INSERT INTO {coll}(pid,'
        for key in obj:
            query += f'{key},'
        query = query[:-1] + f') VALUES({id},'

        gen = _QueryVariableGenerator()

        for v in obj.values():
            query += f'{gen.get_variable(v)},'
        query = query[:-1] + ');'

        print(query)

        async with self._pool.acquire() as conn:
            await conn.execute(query, *gen.variables)


def db_factory(name: str) -> DB or None:
    if name == 'Elasticsearch':
        return ElasticDB()
    elif name == 'Postgres':
        return PostgesDB()

    return None
