from aiohttp import web
from api.routes import routes

if __name__ == '__main__':
    app = web.Application()
    # route part
    for method, route, handler, name in routes:
        app.router.add_route(method, route, handler, name=name)
    web.run_app(app, host='0.0.0.0', port=8080)
