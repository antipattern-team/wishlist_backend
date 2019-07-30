from aiohttp import web
from models import *
import jwt
from settings import auth_key, app_secret
from vkutils import *


def auth_mw(handler):
    async def func(request: web.Request):
        jwt_present = "jwt_token" in request.cookies.keys()
        # 0) check if jwt_token is_valid
        if jwt_present:
            jwt_token = request.cookies.get("jwt_token")
            try:
                decoded_token = jwt.decode(jwt_token, auth_key, algorithms=['HS256'])
            except jwt.exceptions.PyJWTError:
                jwt_present = False
                # 0.5) if not valid, just delete it => rewrite the cookie
                pass

        if jwt_present:
            uid = decoded_token.get("uid")
        else:
            # The needed info is already obtained from frontend request
            # All we need is to check sign validity
            vksign = request.query.get("sign")
            if vksign is None:
                return unauthorized_response()

            vkquery = dict(request.query)
            if not vk_validation(query=vkquery, secret=app_secret):
                return unauthorized_response()

            try:
                uid = await add_user(request)
            except ErrorUnauthorized:
                return unauthorized_response()

            jwt_token = await request.app.auth_connection.call(uid)

        context = {'uid': uid}
        response: web.Response = await handler(request, context)

        if not jwt_present:
            response.set_cookie(name="jwt_token", value=jwt_token)

        return response

    return func
