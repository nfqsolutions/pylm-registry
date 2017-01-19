from urllib import parse
import json

from tornado.testing import AsyncHTTPTestCase
from pylm.registry.application import make_app
from pylm.registry.db import DB

DB.sync_tables()

# Class that holds the temporary server. Note that the tests must be executed
# in strict order.


class TestIndexApp(AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

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
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b"new key")

    def test_07user_wrong(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'new_user',
                             'name': 'New User',
                             'data': '{}',
                             'key': "new key"})),
            headers={'Key': 'wrong_key'})
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, b"Admin key not valid")

    def test_08user_list(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'user_list'})),
            headers={'Key': 'new_key'})
        self.assertEqual(response.code, 200)
        user_list = json.loads(response.body.decode('utf-8'))
        self.assertEqual(user_list[0]["name"], "New User")

    def test_09user(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'user',
                             'key': 'new key'})),
            headers={'Key': 'new_key'})

        self.assertEqual(response.code, 200)
        user_info = json.loads(response.body.decode('utf-8'))
        self.assertEqual(user_info['key'],  'new key')

    def test_10user_key(self):
        response = self.fetch('/admin?{}'.format(
            parse.urlencode({'method': 'new_user',
                             'name': 'some_name',
                             'data': '{"email": "some@email.com"}',
                             'key': 'new key 1'})),
            headers={'Key': 'new_key'})

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body,  b'new key 1')


