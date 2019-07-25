import asyncio
from functools import partial
from aio_pika import connect, IncomingMessage, Exchange, Message


async def auth(msg):  # main authentication
    await asyncio.sleep(int(msg))
    return msg


async def on_message(exchange: Exchange, message: IncomingMessage):
    with message.process():

        msg = message.body.decode()

        # print(f" [.] got({msg})")
        response = str(await auth(msg)).encode()

        await exchange.publish(
            Message(
                body=response,
                correlation_id=message.correlation_id
            ),
            routing_key=message.reply_to
        )
        # print('Request complete')


async def main(loop):
    connection = await connect(  # "amqp://guest:guest@localhost/",
        host="localhost",
        port=5672,
        login='guest',
        password='guest',
        loop=loop
    )

    channel = await connection.channel()

    queue = await channel.declare_queue('auth_queue')

    await queue.consume(
        partial(
            on_message,
            channel.default_exchange
        )
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    # print(" [x] Awaiting RPC requests")
    loop.run_forever()
