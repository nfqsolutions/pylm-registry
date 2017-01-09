from tornado.testing import AsyncHTTPTestCase
from pylm.registry.routes import app


class TestIndexApp(AsyncHTTPTestCase):
    def get_app(self):
        return app

    def test_index(self):
        response = self.fetch('/?something=what', headers={'ho': 'ho'})
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

    def test_admin(self):
        response = self.fetch('/admin')
        self.assertEqual(response.code, 200)
