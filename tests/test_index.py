from urllib import parse
import os
import io
import inspect
import pylm.registry
import pandas as pd

# Set the configuration as the environment variable.

STATIC_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir,
    'static')
    )

# This environment variable is needed at import time
os.environ['PYLM_REGISTRY_CONFIG'] = os.path.join(STATIC_PATH, 'registry.conf')

from tornado.testing import AsyncHTTPTestCase
from pylm.registry.routes import app
from pylm.registry.db import DB

DB.sync_tables()

# Class that holds the temporary server. Note that the tests must be executed
# in strict order.


class TestIndexApp(AsyncHTTPTestCase):
    def get_app(self):
        return app

    def test_00index(self):
        response = self.fetch('/?something=what')
        self.assertEqual(response.code, 200)

    def test_01another(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_03favicon(self):
        response = self.fetch('/favicon.ico')
        self.assertEqual(response.code, 200)

    def test_04admin_set(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'new_admin',
                             'name': 'New Admin Account',
                             'key': 'new_key'})),
            headers={'Key': 'test'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'new_key')

    def test_05admin_wrong(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'new_admin',
                             'name': 'New Admin Account'})
        ))
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, b'Key not present')

    def test_06user_set(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'new_user',
                             'name': 'New User',
                             'data': '{}',
                             'key': "new key"})),
            headers={'Key': 'new_key'})
        self.assertEqual(response.code, 200),
        self.assertEqual(response.body, b"new key")

    def test_07user_wrong(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'new_user',
                             'name': 'New User',
                             'data': '{}',
                             'key': "new key"})),
            headers={'Key': 'wrong_key'})
        self.assertEqual(response.code, 400),
        self.assertEqual(response.body, b"Admin key not valid")

    def test_08user_list(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'user_list'})),
            headers={'Key': 'new_key'})
        self.assertEqual(response.code, 200),
        buffer = io.BytesIO(response.body)
        user_list = pd.read_csv(buffer)
        self.assertEqual(user_list.name[0], "New User")

    def test_10new_cluster(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'new_cluster'})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)