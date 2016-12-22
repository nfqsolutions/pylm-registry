import tornado.web
from pylm.registry.handlers import IndexHandler

app = tornado.web.Application(
    [
        (r"/", IndexHandler)
    ]
)
