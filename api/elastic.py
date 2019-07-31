from elasticsearch_async import AsyncElasticsearch


class Elastic:
    _conn = None
    es_coll = None

    @classmethod
    def init(cls, host: str, es_coll: str):
        cls._conn: AsyncElasticsearch = AsyncElasticsearch(hosts=[host])
        cls.es_coll = es_coll

    @classmethod
    async def save(cls, obj: dict, coll: str, id: int):
        await cls._conn.index(index=coll, id=id, body=obj)

    @classmethod
    def _process(cls, hits):
        processed = []
        for hit in hits:
            obj = hit['_source']
            obj['pid'] = int(hit['_id'])
            processed.append(obj)

        return processed

    @classmethod
    async def _search(cls, coll: str, query: dict, term: dict = None):
        if term:
            objects = (await cls._conn.search(index=coll, body={'query': query, 'size': 100}))['hits']['hits']
            objects = cls._process(objects)
            for t in term:
                objects = [o for o in objects if o[t] == term[t]]
            return objects
        else:
            objects = (await cls._conn.search(index=coll, body={'query': query, 'size': 100}))['hits']['hits']
            return cls._process(objects)

    @classmethod
    async def find_prefix(cls, coll: str, param: str, value: str, term: dict = None):
        return await cls._search(coll=coll, query={'prefix': {param: value}}, term=term)

    @classmethod
    async def find_like(cls, coll: str, param: str, value: str, term: dict = None):
        return await cls._search(coll=coll, query={'match_phrase': {param: value}}, term=term)
