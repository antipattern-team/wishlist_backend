from elasticsearch_async import AsyncElasticsearch


class DB:
    def connect(self, host: str) -> bool:
        pass

    async def drop(self, coll: str) -> None:
        pass

    async def save(self, obj: dict, coll: str, id: int) -> None:
        pass


class ElasticDB(DB):
    def __init__(self):
        self._connection = None

    def connect(self, host: str) -> bool:
        try:
            self._connection = AsyncElasticsearch(hosts=[host])
        except BaseException:
            return False

        return True

    async def drop(self, coll: str) -> None:
        await self._connection.indices.delete(index=coll, ignore=[400, 404])

    async def save(self, obj: dict, coll: str, id: int) -> None:
        await self._connection.index(index=coll, doc_type='_doc', id=id, body=obj)


def db_factory(name: str) -> DB or None:
    if name == 'Elasticsearch':
        return ElasticDB()

    return None
