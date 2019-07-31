import asyncio
from functools import partial
from aio_pika import connect, IncomingMessage, Exchange, Message
import jwt
from settings import *
import time


async def encode(msg):  # main authentication
    encoded_token = jwt.encode({'uid': msg}, auth_key, algorithm='HS256')
    print(f" [.] got({jwt.decode(encoded_token, auth_key, algorithms=['HS256'])})")
    await asyncio.sleep(0.05)
    return encoded_token


async def decode(msg):
    try:
        decoded_token = jwt.decode(msg, auth_key, algorithms=['HS256'])
        print(f" [.] got({decoded_token})")
        await asyncio.sleep(0.05)
    except jwt.exceptions.PyJWTError:
        decoded_token = ""
    return decoded_token


async def on_message(exchange: Exchange, message: IncomingMessage):
    with message.process():

        msg = message.body.decode()

        msg, method = msg.split(sep='.')

        if method == 'encode':
            response = str(await encode(msg))
        elif method == 'decode':
            response = str(await decode(msg))
        else:
            response = ""

        await exchange.publish(
            Message(
                body=response.encode("ascii"),
                correlation_id=message.correlation_id
            ),
            routing_key=message.reply_to
        )
        # print('Request complete')


async def main(loop, host):
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
        )
    )


if __name__ == "__main__":
    if sleep:
        secs = 60
        print(f'Sleeping for {secs} secs')
        time.sleep(secs)
        print('Slept')

    loop = asyncio.get_event_loop()
    loop.create_task(main(loop, rmq_host))
    print(" [x] Awaiting RPC requests")
    loop.run_forever()
