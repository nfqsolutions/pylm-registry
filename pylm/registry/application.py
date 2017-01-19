import argparse
import configparser
import inspect
import os
import sys

import tornado.ioloop
import tornado.web

import pylm.registry

STATIC_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir,
    'static')
    )

# Behave differently if it is executed by py.test
if 'test' in sys.argv[0]:
    STATIC_PATH = os.path.abspath(os.path.join(
        inspect.getfile(pylm.registry),
        os.pardir,
        'static')
    )

    # This environment variable is needed at import time
    PYLM_REGISTRY_CONFIG = os.path.join(STATIC_PATH, 'registry.conf')
    sync = False

else:
    parser = argparse.ArgumentParser(description='Run the PALM registry')
    parser.add_argument('--config', help="path of the configuration file",
                        required=True, type=str)
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--sync', action='store_true')
    parser.set_defaults(sync=False)
    args = parser.parse_args()

    # This environment variable is needed at import time
    PYLM_REGISTRY_CONFIG = args.config
    sync = args.sync

configuration = configparser.ConfigParser()
configuration.read(PYLM_REGISTRY_CONFIG)


def make_app():
    from pylm.registry.handlers import IndexHandler, ClusterHandler, \
        StaticHandler, AdminHandler, LogsHandler
    from pylm.registry.handlers.persistency.db import DB

    app = tornado.web.Application(
        [
            (r"/cluster", ClusterHandler),
            (r"/admin", AdminHandler),
            (r"/logs", LogsHandler),
            (r"/favicon.ico", StaticHandler),
            (r"/", IndexHandler),
        ]
    )
    if sync:
        print('Warning: syncing tables')
        DB.sync_tables()

    return app


def main():
    app = make_app()
    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()