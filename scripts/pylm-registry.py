#!/usr/bin/env python
from pylm.registry.main import app
import tornado.ioloop

if __name__ == '__main__':
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
