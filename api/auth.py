from aiohttp import web

@web.middleware
async def authorize_from_vk(request, handler):
    def check_path(path):  # todo(UsatiyNyan): move this check to routes_add
        result = False
        for r in ['/friends', '/gifts', '/wishlist']:
            if path.startswith(r):
                result = True
        return result

    response = await handler(request)
    if check_path(request.path):
        if 'uid' not in request.cookies.keys():
            response.text += 'ORM_validation + cookie_set'  # todo(UsatiyNyan): redirect to url_for()
            uid = 1  # orm.request()
            response.set_cookie(name='id', value=uid, max_age=60)
            return response
        else:
            response.text += 'already validated'
            return response
    return response
