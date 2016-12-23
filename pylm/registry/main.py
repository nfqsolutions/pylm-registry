import tornado.web
from pylm.registry.handlers import IndexHandler, ClusterHandler

app = tornado.web.Application(
    [
        (r"/cluster", ClusterHandler),
        (r"/", IndexHandler)
    ]
)
