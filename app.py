import logging
from urllib.parse import urljoin

from aiohttp import web, ClientSession

from utils import logger, multidict_to_dict, get_response, directory_is_not_empty, clean_headers
from settings import UPSTREAM


log = logging.getLogger("mocksha")
logging.root.setLevel(logging.INFO)
logging.root.addHandler(logging.StreamHandler())

routes = web.RouteTableDef()

@routes.view(r"/{URN:.*}")
class MyView(web.View):

    async def get(self):

        if UPSTREAM:
            log.info("\nRecord mode. UPSTREAM={}".format(UPSTREAM))
            log.info("{:*^40}\n".format("START"))
            log.info("REQUEST {method} {url}".format(method=self.request.method, url=self.request.url))

            data = {
                "request": {
                    "method": self.request.method,
                    "url": str(self.request.url),
                    "headers": multidict_to_dict(self.request.headers),
                    "queryString" : [{"name": key, "value": value} for key, value in self.request.query.items()],
                },
            }

            target_url = urljoin(UPSTREAM, self.request.path_qs.lstrip("/"))

            log.info("RE-REQUEST {method} {url}".format(method=self.request.method, url=target_url))

            async with ClientSession() as session:
                async with session.get(target_url) as response:
                    text = await response.text()

            log.info("RESPONSE {url} STATUS {status}".format(url=target_url, status=response.status))

            headers = multidict_to_dict(response.headers)
            data.update({
                "response": {
                    "status": response.status,
                    "headers": headers,
                    "content": {
                        "body": text,
                    },
                }
            })

            file_name = logger(data)

            clean_headers(headers)

            if file_name:
                log.info("SAVED RESPONSE (status, headers, content) to {file_name}".format(file_name=file_name))

            log.info("\n{:*^40}\n".format("END"))

            return web.Response(body=text, status=response.status, headers=headers)

        else:
            log.info("\nReplay mode. UPSTREAM={}".format(UPSTREAM))
            log.info("{:*^40}\n".format("START"))
            log.info("REQUEST {method} {url}".format(method=self.request.method, url=self.request.url))
            log.info("RE-REQUEST TO FILE {method} {url}".format(method=self.request.method, url=self.request.url))

            response = get_response(str(self.request.url))

            if not response:
                text = "Text Not Found"
                status = 404
                headers = {"Content-Type": "text/html"}

                log.info("CACHE NOT available (file not found)")
                log.info("RESPONSE {url} STATUS {status}".format(url=self.request.url, status=status))
            else:
                text = response["response"]["content"]["body"]
                status = response["response"]["status"]
                headers = response["response"]["headers"]

                clean_headers(headers)

                log.info("CACHE available in file (first found) {file_name}".format(file_name=response["file_name"]))
                log.info("RESPONSE {url} STATUS {status}".format(url=self.request.url, status=status))

            log.info("\n{:*^40}\n".format("END"))
            return web.Response(body=text, headers=headers, status=status)

    async def post(self):
        pass


async def init_msg(app):

    if directory_is_not_empty():
        raise Exception("The app shouldn't start if config_dir is not empty")

    if UPSTREAM:
        log.info("\n")
        log.info("Record mode - intercepts ans saves HTTP requests to YAML files\n")
    else:
        log.info("\n")
        log.info("Replay mode - serves requests locally from the YAML files\n")


app = web.Application()
app.add_routes(routes)
app.on_startup.append(init_msg)


def init_func(argv):
    app = web.Application()
    app.add_routes(routes)

    return app


if __name__ == "__main__":
    web.run_app(app)
