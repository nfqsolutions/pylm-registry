from urllib import parse
import os
import inspect
import pylm.registry
import json

# Set the configuration as the environment variable.

STATIC_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir,
    'static')
    )

# This environment variable is needed at import time
os.environ['PYLM_REGISTRY_CONFIG'] = os.path.join(STATIC_PATH, 'registry.conf')

from tornado.testing import AsyncHTTPTestCase
from pylm.registry.application import app

cluster = """
[Valuation Master]
Script = valuation_standalone_master.py
--pull = _1
--pub = _2
--workerpull = _3
--workerpush = _4
--db = _5

[Valuation Worker]
Script = valuation_worker.py
--db = _5
Connected = Valuation Master
Role = Worker
Replicas = 1
"""

# Class that holds the temporary server. Note that the tests must be executed
# in strict order.


class TestIndexApp(AsyncHTTPTestCase):
    def get_app(self):
        return app

    def test_00set_cluster(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'new_cluster',
                             'key': 'my cluster',
                             'description': cluster})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'my cluster')

    def test_01send_log(self):
        response = self.fetch('/logs?{}'.format(
            parse.urlencode({
                'cluster': 'my cluster'})),
            method="POST",
            body=b"This is a piece of log")
        self.assertEqual(response.code, 200)

    def test_02query_log(self):
        response = self.fetch('/logs?{}'.format(
            parse.urlencode({
                'cluster': 'my cluster',
            })),
        )
        self.assertEqual(response.code, 200)
        parsed_log = json.loads(response.body.decode('utf-8'))
        self.assertEqual(parsed_log[0]['text'], 'This is a piece of log')