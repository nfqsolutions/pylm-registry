import json
from urllib import parse

from tornado.httpclient import HTTPClient


class LogClient(object):
    """
    Client to send and retrieve logs
    """
    def __init__(self, uri, cluster):
        self.uri = uri
        self.cluster = cluster

    def send(self, text):
        """
        Send a log line to the registry

        :param text: Text of the log line
        """
        arguments = {
            'cluster': self.cluster,
        }
        client = HTTPClient()
        client.fetch('{}/logs?{}'.format(
            self.uri, parse.urlencode(arguments)),
            method='POST',
            body=text.encode('utf-8')
        )

    def download(self, fr=None, to=None):
        """
        Download the log lines, that you may filter by time

        :param fr: datetime. Log lines from
        :param to: datetime. Log lines to
        :return: A list with dicts
        """
        arguments = {
            'cluster': self.cluster
        }

        if fr:
            arguments['fr'] = fr

        if to:
            arguments['to'] = to

        client = HTTPClient()
        response = client.fetch('{}/logs?{}'.format(
            self.uri, parse.urlencode(arguments)),
        )

        return json.loads(response.body.decode('utf-8'))

    def view(self, fr=None, to=None):
        """
        Pretty print the log lines

        :param fr: datetime. Log lines from
        :param to: datetime. Log lines to
        :return:
        """
        for log_line in self.download(fr, to):
            print(log_line['when'], log_line['text'])

    def delete(self):
        raise NotImplementedError()