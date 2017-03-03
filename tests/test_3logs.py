from urllib import parse
import json
from tornado.testing import AsyncHTTPTestCase
from pylm.registry.application import make_app
from datetime import datetime
from pylm.registry.messages.registry_pb2 import LogMessages

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
        return make_app()

    def test_00set_cluster(self):
        response = self.fetch('/cluster?{}'.format(
            parse.urlencode({'method': 'new_cluster',
                             'key': 'my cluster',
                             'description': cluster})),
            headers={'Key': 'new key'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'my cluster')

    def test_01send_log(self):
        msg = LogMessages()
        msg.messages.extend([b"This is a piece of log"])
        response = self.fetch('/logs?{}'.format(
            parse.urlencode({
                'cluster': 'my cluster'})),
            method="POST",
            body=msg.SerializeToString())
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

    def test_03_query_with_dates(self):
        threshold = datetime.now()
        msg = LogMessages()
        msg.messages.extend([b"Log1",
                             b"Log2",
                             b"Log3"])
        response = self.fetch('/logs?{}'.format(
            parse.urlencode({
                'cluster': 'my cluster'})),
            method="POST",
            body=msg.SerializeToString())
        self.assertEqual(response.code, 200)

        response = self.fetch('/logs?{}'.format(
            parse.urlencode({
                'cluster': 'my cluster',
                'fr': threshold.isoformat()
            })),
        )

        parsed_log = json.loads(response.body.decode('utf-8'))
        print('+++++', parsed_log)
        self.assertEqual(parsed_log[0]['text'], 'Log1')
        self.assertEqual(parsed_log[1]['text'], 'Log2')

        response = self.fetch('/logs?{}'.format(
            parse.urlencode({
                'cluster': 'my cluster',
                'to': threshold.isoformat()
            })),
        )

        parsed_log = json.loads(response.body.decode('utf-8'))
        print('+++++', parsed_log)
        self.assertEqual(parsed_log[0]['text'], 'This is a piece of log')

        new_threshold = datetime.now()
        msg = LogMessages()
        msg.messages.extend([b'Another log'])
        response = self.fetch('/logs?{}'.format(
            parse.urlencode({
                'cluster': 'my cluster'})),
            method="POST",
            body=msg.SerializeToString())


        response = self.fetch('/logs?{}'.format(
            parse.urlencode({
                'cluster': 'my cluster',
                'fr': threshold.isoformat(),
                'to': new_threshold.isoformat()
            })),
        )

        parsed_log = json.loads(response.body.decode('utf-8'))
        parsed_log = json.loads(response.body.decode('utf-8'))
        print('+++++', parsed_log)
        self.assertEqual(parsed_log[0]['text'], 'Log1')
        self.assertEqual(parsed_log[1]['text'], 'Log2')
        self.assertEqual(len(parsed_log), 3)
