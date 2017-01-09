from urllib import parse
import os
import inspect
import pylm.registry

# Set the configuration as the environment variable.

STATIC_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir,
    'static')
    )

os.environ['PYLM_REGISTRY_CONFIG'] = os.path.join(STATIC_PATH, 'registry.conf')

from tornado.testing import AsyncHTTPTestCase
from pylm.registry.routes import app
from pylm.registry.db import DB

DB.sync_tables()


class TestIndexApp(AsyncHTTPTestCase):
    def get_app(self):
        return app

    def test_index(self):
        response = self.fetch('/?something=what')
        self.assertEqual(response.code, 200)

    def test_another(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_cluster(self):
        response = self.fetch('/cluster')
        self.assertEqual(response.code, 200)

    def test_favicon(self):
        response = self.fetch('/favicon.ico')
        self.assertEqual(response.code, 200)

    def test_admin_set(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'new',
                             'name': 'New Admin Account',
                             'key': 'new_key'})),
                              headers={'Key': 'test'})
        self.assertEqual(response.code, 200)

    def test_admin_wrong(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'new',
                             'name': 'New Admin Account'})
        ))
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, b'Key not present')

