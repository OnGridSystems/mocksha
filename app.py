import os
from aiohttp import web, ClientSession

from utils import logger, multidict_to_dict, get_response


routes = web.RouteTableDef()

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
                    res = response
                    raw = await res.read()

            headers = dict(res.headers)
            if "Transfer-Encoding" in headers:
                del headers["Transfer-Encoding"]
                headers["Content-Length"] = str(len(raw))

            data.update({
                "response": {
                    "status": res.status,
                    #TODO
                    "headers": multidict_to_dict(response.headers),
                    "content": {
                        "body": raw,
                    },
                }
            })

            logger(data)

            return web.Response(body=raw, status=res.status, headers=headers)

        else:
            response = get_response(str(self.request.url))

            if not response:
                body = "Text Not Found"
                status = 404
                headers = {"Content-Type": "text/html"}
            else:
                body = response["response"]["content"]["body"]
                status = response["response"]["status"]
                headers = response["response"]["headers"]

            return web.Response(body=body, headers=headers, status=status)


    async def post(self):
        pass


app = web.Application()
app.add_routes(routes)

def init_func(argv):
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == "__main__":
    web.run_app(app)
