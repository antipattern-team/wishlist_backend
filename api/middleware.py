from aiohttp import web


@web.middleware
def auth_mw(handler):
    async def func(request):
        # uid = None
        # if 'uid' not in request.cookies.keys():
        #     uid = 1  # RMQ.request()
        #     response.set_cookie(name='uid', value=uid, max_age=60)
        #     print('cookie-set')
        # else:
        #     print('cookie-get')
        #     # ORM.validation()
        context = {}

        if 'token' in request.cookies.keys():
            token = request.cookies['token']
            # todo: send token
            # todo: get uid
            uid = 90000
        else:
            # todo: somehow get vkid
            # todo: send vkid
            # todo: get uid
            # todo: get token
            token = 'token'
            uid = 90000

        context['uid'] = uid
        response = await handler(request, context)

        response.cookies['token'] = token
        return response

    return func
