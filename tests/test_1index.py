from tornado.testing import AsyncHTTPTestCase

from pylm.registry.application import make_app
from pylm.registry.handlers.persistency.db import DB
from pylm.registry.handlers.persistency.models import User

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

    def test_04create_user(self):
        user = User()
        user.key = 'new key'
        user.password = 'xxxx'
        user.name = 'admin'
        user.active = True

        DB.session.add(user)
        DB.session.commit()



