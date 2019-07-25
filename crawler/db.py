from elasticsearch_async import AsyncElasticsearch
import asyncpg


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
        self._connection = None

    async def connect(self, host: str, user: str = '', password: str = '', database: str = '') -> bool:
        try:
            self._connection = await asyncpg.connect(user=user, password=password,
                                                     database=database, host=host)
        except BaseException:
            return False

        return True

    async def drop(self, coll: str) -> None:
        # await self._connection.indices.delete(index=coll, ignore=[400, 404])
        await self._connection.execute(f'TRUNCATE TABLE {coll} CASCADE;')

    async def save(self, obj: dict, coll: str, id: int) -> None:
        # await self._connection.index(index=coll, doc_type='_doc', id=id, body=obj)
        query = f'INSERT INTO {coll}(pid,'
        for key in obj:
            query += f'{key},'
        query = query[:-1] + f') VALUES({id},'

        for value in obj.values():
            if isinstance(value, int):
                query += f'{value},'
            else:
                value = value.replace('\'', '\"')
                query += f'\'{value}\','
        query = query[:-1] + ');'

        print(query)
        await self._connection.execute(query)


def db_factory(name: str) -> DB or None:
    if name == 'Elasticsearch':
        return ElasticDB()
    elif name == 'Postgres':
        return PostgesDB()

    return None
