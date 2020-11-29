from aiohttp import web

from .routes import setup_routes


app = web.Application()

async def create_app():
    app = web.Application()
    setup_routes(app)

    return app
