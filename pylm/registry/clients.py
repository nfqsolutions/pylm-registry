from tornado.httpclient import HTTPClient, HTTPRequest
from urllib import parse


class RegistryClient(object):
    def __init__(self, API_KEY):
        pass


class AdminClient(object):
    def __index__(self, uri, API_KEY):
        self.uri = uri
        self.key = API_KEY

    def new_key(self):
        request = HTTPRequest(self.url, "GET", headers={'Key': 'test'})
        new_uri = parse.urljoin(request, 'admin?new')
        response = HTTPClient.fetch(new_uri)
        print(response)