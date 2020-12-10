from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestServer, Application

from app import init_func
from settings import UPSTREAM
from utils import clean_config_directory


class MockshaAppTestCase(AioHTTPTestCase):

    @classmethod
    def tearDownClass(cls):
        if not UPSTREAM:
            clean_config_directory()

    async def get_server(self, app: Application) -> TestServer:
        """Return a TestServer instance."""
        return TestServer(app, port=8081, loop=self.loop)

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        return init_func(test=True)

    @unittest_run_loop
    async def test_get_version(self):

        resp = await self.client.request("GET", "/api/v1")
        assert resp.status == 200

        data = await resp.json()
        assert data["data"]["version"] == "Lighthouse/v0.3.5-7e4ee5872/x86_64-linux"


    @unittest_run_loop
    async def test_get_parameters(self):

        key = "key1"
        value = "value1"

        resp = await self.client.request("GET", "/api/v1/data", params={key: value})
        assert resp.status == 200

        text = await resp.text()
        assert text == "{}={}".format(key, value)


    @unittest_run_loop
    async def test_post_data(self):

        data = '{"key": "value"}'
        resp = await self.client.request("POST", "/api/v1/post-data", data=data)
        assert resp.status == 200

        text = await resp.text()
        assert text == data


    @unittest_run_loop
    async def test_post_rpc(self):

        URI = "/rpc"

        params = {}
        resp = await self.client.request("POST", URI, json=params)
        assert resp.status == 400

        params = {"jsonrpc": "2.0"}
        resp = await self.client.request("POST", URI, json=params)
        assert resp.status == 400

        params = {"jsonrpc": "2.0", "method": ""}
        resp = await self.client.request("POST", URI, json=params)
        assert resp.status == 400

        params = {"jsonrpc": "2.0", "method": "someThing", "params": []}
        resp = await self.client.request("POST", URI, json=params)
        assert resp.status == 400

        params = {"jsonrpc": "2.0", "method": "", "params": [], "id": 0}
        resp = await self.client.request("POST", URI, json=params)
        assert resp.status == 404

        params = {"jsonrpc": "2.0", "method": "add", "params": [5, 7], "id": 0}
        resp = await self.client.request("POST", URI, json=params)
        assert resp.status == 200

        json = await resp.json()
        assert json["result"] == params["params"][0] + params["params"][1]

        params = {"jsonrpc": "2.0", "method": "subtract", "params": [5, 7], "id": 0}
        resp = await self.client.request("POST", URI, json=params)
        assert resp.status == 200

        json = await resp.json()
        assert json["result"] == params["params"][0] - params["params"][1]
