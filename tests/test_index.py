from tornado.testing import AsyncHTTPTestCase
from pylm.registry.main import app


class TestIndexApp(AsyncHTTPTestCase):
    def get_app(self):
        return app

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
