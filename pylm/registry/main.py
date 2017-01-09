import tornado.web
from pylm.registry.handlers import IndexHandler, ClusterHandler, StaticHandler

app = tornado.web.Application(
    [
        (r"/cluster", ClusterHandler),
        (r"/favicon.ico", StaticHandler),
        (r"/", IndexHandler),
    ]
)

