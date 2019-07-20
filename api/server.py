from aiohttp import web
from routes import routes
from auth import authorize_from_vk

if __name__ == '__main__':
    app = web.Application(middlewares=[authorize_from_vk])
    # route part
    for method, route, handler, name in routes:
        app.router.add_route(method, route, handler, name=name)
    web.run_app(app, host='0.0.0.0', port=8080)
