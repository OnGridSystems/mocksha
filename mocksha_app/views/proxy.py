from aiohttp import web
import aiohttp


async def index(request):

    url = request.rel_url.query["url"]
    print(url)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            status = response.status
            headers = response.headers
            html = await response.text()

    return web.Response(text=html, status=status, headers={"content_type": "text/html"})
