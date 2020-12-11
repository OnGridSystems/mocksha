from asynctest import patch

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, make_mocked_request, make_mocked_coro

from mocksha.app import handler, init_func


class UnitTestCase(AioHTTPTestCase):

    # async def setUpAsync(self):
    #     self.patcher = mock.patch("mocksha.app.http_client", return_value="Body")
    #     self.patcher.start()
    #
    # async def tearDownAsync(self):
    #     self.patcher.start()

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        return init_func(test=True)

    @patch("aiohttp.client.ClientSession.request")
    @unittest_run_loop
    async def test_handler(self, mock_output):

        class Response:
            def __init__(self, method, url, text, headers, status):
                self.method = method
                self.url = url
                self.text = text
                self.headers = headers
                self.status = status

        mock_response = Response(method="GET", url="/", text=make_mocked_coro("Body"), headers={}, status=200)
        mock_output.return_value.__aenter__.return_value = mock_response

        req = make_mocked_request("GET", "/")
        req.text = make_mocked_coro("Body")
        resp = await handler(req)

        assert resp.status == 200
