import argparse
import inspect
import tornado.ioloop
import pylm.registry
import os

STATIC_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir,
    'static')
    )

parser = argparse.ArgumentParser(description='Run the PALM registry')
parser.add_argument('--port', type=int, default=8080)
parser.add_argument('--config', type=str,
                    default=os.path.join(STATIC_PATH, 'registry.conf'))
parser.add_argument('--sync', action='store_true')
parser.set_defaults(sync=False)
args = parser.parse_args()

# This environment variable is needed at import time
os.environ['PYLM_REGISTRY_CONFIG'] = args.config

from pylm.registry.application import app
from pylm.registry.db import DB

if args.sync:
    print('Warning: syncing tables')
    DB.sync_tables()


def main():
    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()
