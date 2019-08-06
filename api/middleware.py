from vkutils import *
import ast


def auth_mw(handler):
    async def func(request: web.Request):
        jwt_present = "jwt_token" in request.cookies.keys()
        # 0) check if jwt_token is_valid
        if jwt_present:
            jwt_token = request.cookies.get("jwt_token")
            decoded_token = await request.app.auth_connection.call(jwt_token, 'decode')
            if decoded_token is None:  # 0.5) if not valid, just delete it => rewrite the cookie
                jwt_present = False

        if jwt_present:
            decoded_token = ast.literal_eval(decoded_token)
            uid = decoded_token.get("uid")
        else:
            return unauthorized_response()

        context = {'uid': uid}
        response = await handler(request, context)

        return response

    return func
