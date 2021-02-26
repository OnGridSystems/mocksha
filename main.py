from aiohttp import web

routes = web.RouteTableDef()
import os


# @routes.get("/api/v1")
# async def api_version(request):
#
#     return web.json_response({"data": {"version": "Lighthouse/v0.3.5-7e4ee5872/x86_64-linux"}})
#
#
# @routes.get("/api/v1/data")
# async def get_data(request):
#
#     value = request.rel_url.query["key1"]
#     return web.Response(text="key1={}".format(value))
#
#
# @routes.post("/api/v1/post-data")
# async def post_data(request):
#
#     text = await request.text()
#     return web.Response(text=text)


@routes.post("/")
async def rpc(request):
    rpc_format = {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
    rpc_format = set(rpc_format)

    try:
        req = await request.json()
        if req["jsonrpc"] != "2.0":
            raise Exception("jsonrpc version not support")
    except Exception as e:
        return web.json_response({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None},
                                 status=400)

    if rpc_format != set(req):
        return web.json_response({"jsonrpc": "2.0", "error":
            {"code": -32600, "message": "Invalid JSON-RPC."}, "id": None},
                                 status=400)
    else:
        resp = {"jsonrpc": "2.0", "result": 1, "error": None, "id": req["id"]}
        status = 200
        # функции на другие методы //
        if req["method"] == "subtract":
            result = req["params"][0] - req["params"][1]
            resp.update({"result": result})
        elif req["method"] == "add":
            result = req["params"][0] + req["params"][1]
            resp.update({"result": result})
        # \\
        else:
            myreq = 'curl -X POST -H "Content-Type: application/json" -d "{}" {}'.format(req, "http://127.0.0.1:8545")
            resp = os.system(myreq)
        return web.json_response(resp, status=status)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host='0.0.0.0', port=8546)
