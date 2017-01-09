import tornado.web
from pylm.registry.handlers import IndexHandler, ClusterHandler, StaticHandler, AdminHandler

app = tornado.web.Application(
    [
        (r"/cluster", ClusterHandler),
        (r"/admin", AdminHandler),
        (r"/favicon.ico", StaticHandler),
        (r"/", IndexHandler),
    ]
)

