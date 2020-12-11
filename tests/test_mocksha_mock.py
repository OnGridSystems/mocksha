from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from mocksha.app import MyView

def handler(request):
    assert request.headers.get('token') == 'x'
    return web.Response(body=b'data')

# def test_handler():
#     req = make_mocked_request('GET', '/', headers={'token': 'x'})
#     resp = handler(req)
#     assert resp.body == b'data'

def test_handler():
    req = make_mocked_request('GET', '/', headers={'token': 'x'})
    resp = MyView.get(req)
    assert resp.body == b'data'