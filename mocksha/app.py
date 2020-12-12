from urllib.parse import urljoin

from aiohttp import web, ClientSession

from .utils import logger, multidict_to_dict, get_response, directory_is_not_empty, reset_some_response_headers, \
    clean_config_directory
from .settings import UPSTREAM, log


routes = web.RouteTableDef()

@routes.view(r"/{URN:.*}")
class MyView(web.View):

    async def get(self):

        if UPSTREAM:
            log.info("\nRecord mode. UPSTREAM={}".format(UPSTREAM))
            log.info("{:*^40}\n".format("START"))

            text = await self.request.text()

            log.info("REQUEST {method} {url}".format(method=self.request.method, url=self.request.url))
            log.info("REQUEST BODY {text}".format(text=text))

            headers = multidict_to_dict(self.request.headers)
            if "Host" in headers:
                del headers["Host"]

            data = {
                "request": {
                    "method": self.request.method,
                    "url": str(self.request.url),
                    "headers": multidict_to_dict(self.request.headers),
                    "content": {
                        "body": text,
                    }
                },
            }

            target_url = urljoin(UPSTREAM, self.request.path_qs.lstrip("/"))

            log.info("RE-REQUEST {method} {url}".format(method=self.request.method, url=target_url))

            async with ClientSession() as session:
                async with session.get(target_url, data=text, headers=headers) as response:

                    text = await response.text()

            log.info("RESPONSE {url} STATUS {status}".format(url=target_url, status=response.status))
            log.info("RESPONSE BODY {text}".format(text=text))

            headers = multidict_to_dict(response.headers)
            reset_some_response_headers(headers)

            data.update({
                "response": {
                    "url": str(response.url),
                    "status": response.status,
                    "method": response.method,
                    "headers": headers,
                    "content": {
                        "body": text,
                    },
                }
            })

            file_name = logger(data)
            if file_name:
                log.info("SAVED RESPONSE (status, headers, content) to {file_name}".format(file_name=file_name))

            log.info("\n{:*^40}\n".format("END"))
            return web.Response(text=text, status=response.status, headers=headers)

        else:
            log.info("\nReplay mode. UPSTREAM={}".format(UPSTREAM))
            log.info("{:*^40}\n".format("START"))

            text = await self.request.text()

            log.info("REQUEST {method} {url}".format(method=self.request.method, url=self.request.url))
            log.info("REQUEST BODY {text}".format(text=text))
            log.info("RE-REQUEST TO FILE {method} {url}".format(method=self.request.method, url=self.request.url))

            response = get_response(str(self.request.url), text)

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

                log.info("CACHE available in file (first found) {file_name}".format(file_name=response["file_name"]))
                log.info("RESPONSE BODY {text}".format(text=text))
                log.info("RESPONSE {url} STATUS {status}".format(url=self.request.url, status=status))

            log.info("\n{:*^40}\n".format("END"))
            return web.Response(text=text, headers=headers, status=status)

    async def post(self):

        if UPSTREAM:
            log.info("\nRecord mode. UPSTREAM={}".format(UPSTREAM))
            log.info("{:*^40}\n".format("START"))

            text = await self.request.text()

            log.info("REQUEST {method} {url}".format(method=self.request.method, url=self.request.url))
            log.info("REQUEST BODY {text}".format(text=text))

            headers = multidict_to_dict(self.request.headers)
            if "Host" in headers:
                del headers["Host"]

            data = {
                "request": {
                    "method": self.request.method,
                    "url": str(self.request.url),
                    "headers": multidict_to_dict(self.request.headers),
                    "content": {
                        "body": text,
                    }
                },
            }

            target_url = urljoin(UPSTREAM, self.request.path_qs.lstrip("/"))

            log.info("RE-REQUEST {method} {url}".format(method=self.request.method, url=target_url))

            async with ClientSession() as session:
                async with session.post(target_url, data=text, headers=headers) as response:

                    text = await response.text()

            log.info("RESPONSE {url} STATUS {status}".format(url=target_url, status=response.status))
            log.info("RESPONSE BODY {text}".format(text=text))

            headers = multidict_to_dict(response.headers)
            reset_some_response_headers(headers)

            data.update({
                "response": {
                    "url": str(response.url),
                    "status": response.status,
                    "method": response.method,
                    "headers": headers,
                    "content": {
                        "body": text,
                    },
                }
            })

            file_name = logger(data)
            if file_name:
                log.info("SAVED RESPONSE (status, headers, content) to {file_name}".format(file_name=file_name))

            log.info("\n{:*^40}\n".format("END"))
            return web.Response(text=text, status=response.status, headers=headers)

        else:
            log.info("\nReplay mode. UPSTREAM={}".format(UPSTREAM))
            log.info("{:*^40}\n".format("START"))

            text = await self.request.text()

            log.info("REQUEST {method} {url}".format(method=self.request.method, url=self.request.url))
            log.info("REQUEST BODY {text}".format(text=text))
            log.info("RE-REQUEST TO FILE {method} {url}".format(method=self.request.method, url=self.request.url))

            response = get_response(str(self.request.url), text)

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

                log.info("CACHE available in file (first found) {file_name}".format(file_name=response["file_name"]))
                log.info("RESPONSE BODY {text}".format(text=text))
                log.info("RESPONSE {url} STATUS {status}".format(url=self.request.url, status=status))

            log.info("\n{:*^40}\n".format("END"))
            return web.Response(text=text, headers=headers, status=status)


async def startup(app):

    if UPSTREAM:
        if directory_is_not_empty():
            clean_config_directory()

        log.info("\n")
        log.info("Record mode - intercepts ans saves HTTP requests to YAML files\nUPSTREAM={}\n".format(UPSTREAM))
    else:
        if not directory_is_not_empty():
            raise Exception("The app shouldn't start if config_dir is not empty")

        log.info("\n")
        log.info("Replay mode - serves requests locally from the YAML files\nUPSTREAM={}\n".format(UPSTREAM))


def init_func(test=None):
    app = web.Application()
    app.add_routes(routes)
    if not test:
        app.on_startup.append(startup)

    return app
