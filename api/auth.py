from aiohttp import web

@web.middleware
async def authorize_from_vk(request, handler):
    def check_path(path):
        result = False
        for r in ['/friends', '/gifts', '/wishlist']:
            if path.startswith(r):
                result = True
        return result
    if check_path(request.path):
        response = await handler(request)
        if 'id' not in request.cookies.keys():
            response.text += 'ORM_validation + cookie_set'
            id = 1  # orm.request()
            response.set_cookie(name='id', value=id, max_age=60)
            return response
        else:
            response.text += 'already validated'
            return response
    return await handler(request)