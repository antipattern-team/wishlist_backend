import jwt
from settings import auth_key
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
            return unauthorized_response()

        context = {'uid': uid}
        response = await handler(request, context)

        return response

    return func
