from .views import proxy


def setup_routes(app):
    app.router.add_route("GET", "/", proxy.index)
