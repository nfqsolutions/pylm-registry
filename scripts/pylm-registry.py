#!/usr/bin/env python
from pylm.registry.routes import app
import argparse
import tornado.ioloop

parser = argparse.ArgumentParser(description='Run the PALM registry')
parser.add_argument('--port', type=int, default=8080)
args = parser.parse_args()


if __name__ == '__main__':
    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()
