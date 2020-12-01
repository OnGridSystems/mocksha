import os
from aiohttp import web, ClientSession

from utils import logger, multidict_to_dict


routes = web.RouteTableDef()

# UPSTREAM = os.environ.get("UPSTREAM", "http://localhost:5000/api")
UPSTREAM = os.environ.get("UPSTREAM")


@routes.view(r"/{URN:.*}")
class MyView(web.View):

    async def get(self):

        if UPSTREAM:
            print("UPSTREAM!")
            data = {
                "request": {
                    "method": self.request.method,
                    "url": str(self.request.url),
                    "headers": multidict_to_dict(self.request.headers),
                    "queryString" : [{"name": key, "value": value} for key, value in self.request.query.items()],
                },
            }

            # re-request
            async with ClientSession() as session:
                async with session.get(UPSTREAM+self.request.path_qs) as response:

                    text = await response.text()
                    data.update({
                        "response": {
                            "status": response.status,
                            "headers": multidict_to_dict(response.headers),
                            "content": {
                                "text": text,
                            },
                        }
                    })

            logger(data)

            return web.Response(text=text, headers=response.headers, status=response.status)

        else:
            print(self.request.url)
            print(self.request.path_qs)

    async def post(self):
        pass


app = web.Application()
app.add_routes(routes)

def init_func(argv):
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    web.run_app(app)
