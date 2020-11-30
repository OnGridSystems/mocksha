import os, datetime
from aiohttp import web, ClientSession

from .utils import logger

routes = web.RouteTableDef()

@routes.view(r"/{name:.*}")
class MyView(web.View):
    async def get(self):

        data = {
            # TODO
            "request": {
                "method": self.request.method,
                "url": str(self.request.url),
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": [
                    {
                        "name": "Accept-Encoding",
                        "value": "gzip,deflate",
                        "comment": ""
                    },
                    {
                        "name": "Accept-Language",
                        "value": "en-us,en;q=0.5",
                        "comment": ""
                    }
                ],
                "queryString" : [],
                "postData" : {},
                "headersSize" : None,
                "bodySize" : None,
                "comment" : "",
            },
        }


        # re-request
        remote_host = os.environ.get("UPSTREAM", "http://localhost:5000/api")
        async with ClientSession() as session:
            async with session.get(remote_host+self.request.path_qs) as response:

                print(response.status)
                print(response.headers)
                text = await response.text()
                # TODO
                data.update({
                    "response": {
                        "status": 200,
                        "statusText": "OK",
                        "httpVersion": "HTTP/1.1",
                        "cookies": [],
                        "headers": [
                            {
                                "name": "Accept-Encoding",
                                "value": "gzip,deflate",
                                "comment": ""
                            },
                            {
                                "name": "Accept-Language",
                                "value": "en-us,en;q=0.5",
                                "comment": ""
                            }
                        ],
                        "content": {
                            "size": 33,
                            "compression": 0,
                            "mimeType": "text/html; charset=utf-8",
                            "text": text,
                            "comment": ""
                        },
                        "redirectURL": "",
                        "headersSize" : 160,
                        "bodySize" : 850,
                        "comment" : ""
                        }
                })

        logger(data)

        return web.Response(text=text, headers={"content_type": "text/html"}, status=response.status)

    async def post(self):
        pass
