from aiohttp import web


@web.middleware
def auth_mw(handler):
    async def func(request):
        response = await handler(request)
        if 'uid' not in request.cookies.keys():
            uid = 1  # RMQ.request()
            response.set_cookie(name='uid', value=uid, max_age=60)
            print('cookie-set')
            return response
        else:
            print('cookie-get')
            # ORM.validation()
            return response

    return func
