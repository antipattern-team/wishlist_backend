import asyncio
from functools import partial
from aio_pika import connect, IncomingMessage, Exchange, Message
import jwt
import os
import time


async def auth(msg, key):  # main authentication
    encoded_token = jwt.encode({'uid': msg}, key, algorithm='HS256')
    print(f" [.] got({jwt.decode(encoded_token, '123', algorithms=['HS256'])})")
    await asyncio.sleep(0.05)
    return encoded_token


async def on_message(exchange: Exchange, key, message: IncomingMessage):
    with message.process():

        msg = message.body.decode()

        response = str(await auth(msg, key))

        await exchange.publish(
            Message(
                body=response.encode("ascii"),
                correlation_id=message.correlation_id
            ),
            routing_key=message.reply_to
        )
        # print('Request complete')


async def main(loop, key, host):
    connection = await connect(  # "amqp://guest:guest@localhost/",
        host=host,
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
            channel.default_exchange,
            key
        )
    )


if __name__ == "__main__":
    key = '123'
    if 'AUTH_KEY' in os.environ:
        key = bool(os.environ['AUTH_KEY'])

    sleep = False
    if 'SLEEP' in os.environ:
        sleep = bool(os.environ['SLEEP'])

    rmq_host = 'localhost'
    if 'RMQHOST' in os.environ:
        rmq_host = os.environ['RMQHOST']

    if sleep:
        secs = 60
        print(f'Sleeping for {secs} secs')
        time.sleep(secs)
        print('Slept')

    loop = asyncio.get_event_loop()
    loop.create_task(main(loop, key, rmq_host))
    print(" [x] Awaiting RPC requests")
    loop.run_forever()
