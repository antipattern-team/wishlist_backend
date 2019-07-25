import asyncio
import uuid
from aio_pika import connect, IncomingMessage, Message


class AuthRpcClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}
        self.loop = asyncio.get_running_loop()

    async def connect(self):
        self.connection = await connect(  # "amqp://guest:guest@localhost/",
            host="localhost",
            port=5672,
            login='guest',
            password='guest',
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

    async def call(self, n):
        correlation_id = str(uuid.uuid4())
        future = asyncio.get_running_loop().create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                str(n).encode(),
                content_type='text/plain',
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key='auth_queue',
        )

        return int(await future)


async def _main():
    auth_rpc = await AuthRpcClient().connect()
    uid = 12
    print(f" [x] Requesting auth{uid}")
    response = await auth_rpc.call(uid)
    print(f" [.] Got {response}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main())
