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


class TestIndexApp(AsyncHTTPTestCase):
    def get_app(self):
        return app

    def test_01set_cluster(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'new_cluster'})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)