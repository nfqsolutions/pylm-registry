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
from pylm.registry.routes import app

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

server = """
[DEFAULT]
Name = My Worker
Ip = 127.0.0.1
Processors = 3
Ports_from = 5555
"""

server1 = """
[DEFAULT]
Name = My Worker
Ip = 127.0.0.1
Processors = 1
Ports_from = 5555
"""
server2 = """
[DEFAULT]
Name = My Worker
Ip = 127.0.0.2
Processors = 2
Ports_from = 5555
"""


class TestIndexApp(AsyncHTTPTestCase):
    def get_app(self):
        return app

    def test_01set_cluster(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'new_cluster',
                             'key': 'my cluster',
                             'description': cluster})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'my cluster')

    def test_02list_clusters(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'clusters_list'})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body[:13], b'{"my cluster"')

    def test_03simple_request(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'node_config',
                             'cluster': 'my cluster',
                             'node': server})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)
        commands = json.loads(response.body.decode('utf-8'))
        self.assertEqual(commands[0][:7], 'python3')

    def test_04reset_cluster(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'cluster_reset',
                             'cluster': 'my cluster'})),
            headers={'Key': 'new key'})
        print(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'my cluster')

    def test_05multiple_request(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'node_config',
                             'cluster': 'my cluster',
                             'node': server1})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)
        commands = json.loads(response.body.decode('utf-8'))
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][:30], 'python3 valuation_standalone_m')

        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'node_config',
                             'cluster': 'my cluster',
                             'node': server2})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)
        commands = json.loads(response.body.decode('utf-8'))
        print(response)
        self.assertEqual(commands[0][:27], 'python3 valuation_worker.py')
        self.assertEqual(commands[1][:27], 'python3 valuation_worker.py')

    def test_06status_cluster(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'cluster_status',
                             'cluster': 'my cluster'})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)

        cluster_status = json.loads(response.body.decode('utf-8'))
        self.assertEqual(cluster_status["socket mapping"]["_1"], 'tcp://127.0.0.1:5555')

    def test_07delete_cluster(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'cluster_delete',
                             'cluster': 'my cluster'})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'my cluster')
