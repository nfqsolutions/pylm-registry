import argparse
import inspect
import os
import sys
from uuid import uuid4
from collections import namedtuple

import tornado.ioloop
import tornado.web

import pylm.registry

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

import getpass

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
    args_type = namedtuple('Arguments', ['db', 'debug'])
    args = args_type(db='sqlite://', debug=False)

else:
    parser = argparse.ArgumentParser(description='Run the PALM registry')
    parser.add_argument('--db', help="SQLAlchemy database string",
                        type=str, default="sqlite://")
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--sync', action='store_true')
    parser.add_argument('--debug', action='store_true', default=False)
    parser.set_defaults(sync=False)

    args = parser.parse_args()
    sync = args.sync


def make_app():
    from pylm.registry.handlers import IndexHandler, ClusterHandler, \
        StaticHandler, LogsHandler, LoginHandler
    from pylm.registry.handlers.persistency.db import DB
    from pylm.registry.handlers.persistency.models import User

    app = tornado.web.Application(
        [
            (r"/cluster", ClusterHandler),
            (r"/logs", LogsHandler),
            (r"/favicon.ico", StaticHandler),
            (r"/login", LoginHandler),
            (r"/", IndexHandler),
        ],
        cookie_secret="__TODO:_GENERATE_A_RANDOM_KEY_HERE__",
        secret="__TODO:_GENERATE_A_RANDOM_KEY_HERE__",
        login_url="/login",
        db=args.db,
        debug=args.debug
    )
    if sync:
        print('Warning: syncing tables')
        DB.sync_tables()

        if not DB.session.query(User).filter(User.admin==True).all():
            print('No admin available, please setup an admin account:')
            key = str(uuid4())
            password = getpass.getpass('Password: ')

            new_admin = User()
            new_admin.name = 'admin'
            new_admin.full_name = 'Administrator account'
            new_admin.key = key
            new_admin.admin = True
            new_admin.active = True

            backend = default_backend()

            kpdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=os.urandom(16),
                iterations=1000000,
                backend=backend
            )
            new_admin.password = kpdf.derive(password.encode('utf-8'))
            DB.session.add(new_admin)
            DB.session.commit()

            print('Admin account set successfully')

    return app


def main():
    app = make_app()
    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()