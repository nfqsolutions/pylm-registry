import tornado.web
from pylm.registry.handlers import IndexHandler, ClusterHandler,\
    StaticHandler, AdminHandler, LogsHandler

app = tornado.web.Application(
    [
        (r"/cluster", ClusterHandler),
        (r"/admin", AdminHandler),
        (r"/logs", LogsHandler),
        (r"/favicon.ico", StaticHandler),
        (r"/", IndexHandler),
    ]
)

