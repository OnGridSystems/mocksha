from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestServer, Application

from mocksha.app import init_func
from mocksha.settings import UPSTREAM
from mocksha.utils import clean_config_directory


class MockshaAppUseRemoteMockTestCase(AioHTTPTestCase):

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
    async def test_get(self):

        resp = await self.client.request("GET", "/posts/1")
        assert resp.status == 200

        # data = await resp.json()
        # assert data["data"]["version"] == "Lighthouse/v0.3.5-7e4ee5872/x86_64-linux"


    # @unittest_run_loop
    # async def test_get_parameters(self):
    #
    #     key = "key1"
    #     value = "value1"
    #
    #     resp = await self.client.request("GET", "/api/v1/data", params={key: value})
    #     assert resp.status == 200
    #
    #     text = await resp.text()
    #     assert text == "{}={}".format(key, value)
    #
    #
    # @unittest_run_loop
    # async def test_post_data(self):
    #
    #     data = '{"key": "value"}'
    #     resp = await self.client.request("POST", "/api/v1/post-data", data=data)
    #     assert resp.status == 200
    #
    #     text = await resp.text()
    #     assert text == data
