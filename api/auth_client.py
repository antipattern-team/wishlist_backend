import asyncio
import uuid
from aio_pika import connect, IncomingMessage, Message
import ast


class AuthRpcClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}
        self.loop = asyncio.get_running_loop()

    async def connect(self, host):
        self.connection = await connect(  # "amqp://guest:guest@localhost/",
            host=host,
            loop=asyncio.get_running_loop()
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(
            exclusive=True
        )
        await self.callback_queue.consume(self.on_response)

        return self

    def on_response(self, message: IncomingMessage):
        future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, msg, method):
        msg = str(msg) + '/' + method
        correlation_id = str(uuid.uuid4())
        future = asyncio.get_running_loop().create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                str(msg).encode(),
                content_type='text/plain',
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key='auth_queue',
        )

        response: bytes = await future
        response_str = response.decode()
        if response_str.startswith("b'"):
            response_str = response_str[2:-1]
        if response_str == "None":
            return None
        return response_str


async def _test():
    auth_rpc = await AuthRpcClient().connect(host="localhost")
    uid = "1234564546454"
    print(f" [x] Requesting encode {uid}")
    response_str = await auth_rpc.call(uid, "encode")
    print(f" [.] Got {response_str}")
    print(f" [x] Requesting decode {response_str}")
    token = await auth_rpc.call(response_str, "decode")
    token = ast.literal_eval(token)
    print(f" [.] Got {token, type(token)}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_test())