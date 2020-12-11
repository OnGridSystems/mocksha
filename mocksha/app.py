import os
import yaml

from urllib.parse import urljoin

from aiohttp import web, ClientSession

from .utils import reset_some_response_headers, multidict_to_dict, gen_log_file_name, directory_is_not_empty, \
    clean_config_directory
from .settings import log, CONFIG_DIR, UPSTREAM


routes = web.RouteTableDef()


async def http_client(method, target_url, data, headers):
    async with ClientSession() as session:
        async with session.request(method, target_url, headers=headers, data=data, ) as response:
            text = await response.text()

        response_headers = multidict_to_dict(response.headers)
        reset_some_response_headers(response_headers)
        d = {
                "url": str(response.url),
                "status": response.status,
                "method": response.method,
                "headers": response_headers,
                "content": {
                    "body": text,
                    }
                }

        return d

async def sub_request(data_stream):
    if "Host" in data_stream["request"]["headers"]:
        del data_stream["request"]["headers"]["Host"]

    response = await http_client(data_stream["request"]["method"],
                           data_stream["request"]["target_url"],
                           data_stream["request"]["content"]["body"],
                           data_stream["request"]["headers"]
                           )
    data_stream.update({"response": response})

    log.info("RESPONSE {url} STATUS {status}".format(url=data_stream["response"]["url"],
                                                     status=data_stream["response"]["status"]))
    log.info("RESPONSE BODY {text}".format(text=data_stream["response"]["content"]["body"]))

    return data_stream

def save_to_yaml_file(json_data):
    log_file = gen_log_file_name()

    with open(os.path.join(CONFIG_DIR, log_file), "w") as f:
        yaml.dump(json_data, f, default_flow_style=False)
        log.info("SAVED (status, headers, content) to {file_name}".format(file_name=log_file))
        return log_file

def read_yaml_file(json_data):
    log_files = (file for file in os.listdir(CONFIG_DIR) if os.path.isfile(os.path.join(CONFIG_DIR, file)))

    for file in log_files:
        log.info("Reading {}".format(file))
        with open(os.path.join(CONFIG_DIR, file), "r") as f:
            data = yaml.safe_load(f)
            try:
                if data["request"]["url"] == json_data["request"]["url"] \
                    and data["request"]["content"]["body"] == json_data["request"]["content"]["body"]:

                    log.info("READ file (first found) {file_name}".format(file_name=file))
                    return data
            except KeyError:
                raise KeyError("Not valid yaml file")

def cache_dump(data_stream):
    file_name = save_to_yaml_file(data_stream)
    return file_name

def cache_load(data_stream):
    return read_yaml_file(data_stream)

async def proxy(mode, data_stream):
    log.info("\nRecord mode. UPSTREAM={}".format(mode))
    log.info("{:*^40}\n".format("START"))
    log.info("REQUEST {method} {url}".format(method=data_stream["request"]["method"],
                                             url=data_stream["request"]["url"]))
    log.info("REQUEST BODY {text}".format(text=data_stream["request"]["content"]["body"]))

    if mode:
        log.info("RE-REQUEST {method} {url}".format(method=data_stream["request"]["method"],
                                                    url=data_stream["request"]["target_url"]))

        data_stream = await sub_request(data_stream)
        storage = cache_dump(data_stream)
        log.info("SAVED RESPONSE (status, headers, content) to {storage}".format(storage=storage))
        return data_stream
    else:
        log.info("RE-REQUEST TO CACHE {method} {url}".format(method=data_stream["request"]["method"],
                                                             url=data_stream["request"]["url"]))
        cache = cache_load(data_stream)
        if not cache:
            d = {"response":
                    {
                        "content": {"body": "Text Not Found"},
                        "status": 404,
                        "headers": {"Content-Type": "text/html"},
                    }
                }

            log.info("CACHE NOT available")
            log.info("RESPONSE {url} STATUS {status}".format(url=data_stream["request"]["url"],
                                                             status=d["response"]["status"]))
            return d
        else:
            log.info("RESPONSE BODY {text}".format(text=cache["response"]["content"]["body"]))
            log.info("RESPONSE {url} STATUS {status}".format(url=cache["response"]["url"],
                                                             status=cache["response"]["status"]))

            return cache

async def handler(request):
    text = await request.text()

    data_stream = {
        "request": {
            "method": request.method,
            "url": str(request.url),
            "target_url": urljoin(UPSTREAM, request.path_qs.lstrip("/")),
            "headers": multidict_to_dict(request.headers),
            "content": {
                "body": text,
            }
        },
    }

    response = await proxy(mode=UPSTREAM, data_stream=data_stream)
    log.info("\n{:*^40}\n".format("END"))
    return web.Response(text=response["response"]["content"]["body"],
                        status=response["response"]["status"],
                        headers=response["response"]["headers"],
                        )

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
    app.add_routes([web.route("*", r"/{URN:.*}", handler)])

    if not test:
        app.on_startup.append(startup)

    return app
