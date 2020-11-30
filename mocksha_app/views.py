import os
from aiohttp import web, ClientSession

from .utils import logger_request, logger_response

routes = web.RouteTableDef()

@routes.view("/{name}")
class MyView(web.View):
    async def get(self):

        logger_request(self.request)

        remote_host = os.environ.get("UPSTREAM", "http://localhost:5000/api")

        async with ClientSession() as session:
            async with session.get(remote_host+self.request.path_qs) as response:

                text = await response.text()
                logger_response(response, text)

        return web.Response(text=text, headers={"content_type": "text/html"}, status=response.status)

    async def post(self):
        pass
