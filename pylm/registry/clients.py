from tornado.httpclient import HTTPClient
from urllib import parse
import pandas as pd
import io


def new_admin_account(uri, master_key, admin_name, key=None):
    arguments = {
        'method': 'new_admin',
        'name': admin_name,
    }
    if key:
        arguments['key'] = key

    client = HTTPClient()
    response = client.fetch('{}/admin?{}'.format(
        uri, parse.urlencode(arguments)),
        headers={'Key': master_key}
    )
    if response.code == 200:
        return response.body.decode('utf-8')
    else:
        raise ValueError(response.body.decode('utf-8'))


class AdminClient(object):
    """
    Admin client to manage users
    """
    def __init__(self, uri, admin_key):
        self.uri = uri
        self.ak = admin_key

    def new_user(self, name, data={}, key=None):
        arguments = {
            'method': 'new_user',
            'name': name,
            'data': data
        }
        if key:
            arguments[key] = key

        client = HTTPClient()
        response = client.fetch('{}/admin?{}'.format(
            self.uri, parse.urlencode(arguments)),
            headers={'Key': self.ak}
        )
        if response.code == 200:
            return response.body.decode('utf-8')
        else:
            raise ValueError(response.body.decode('utf-8'))

    def user_list(self):
        arguments = {
            'method': 'user_list'
        }

        client = HTTPClient()
        response = client.fetch('{}/admin?{}'.format(
            self.uri, parse.urlencode(arguments)),
            headers={'Key': self.ak}
        )

        if response.code == 200:
            buffer = io.BytesIO(response.body)
            user_list = pd.read_csv(buffer)
            return user_list

        else:
            raise ValueError(response.body.decode('utf-8'))


class RegistryClient(object):
    """
    Registry client to manage users.
    """
    def __init__(self, uri, user_key):
        self.uri = uri
        self.uk = user_key

    def set_cluster(self, config_file, key=None):
        with open(config_file) as f:
            cluster = f.read()

        arguments = {
            'method': 'new_cluster',
            'description': cluster
        }

        if key:
            arguments['key'] = key

        client = HTTPClient()
        response = client.fetch('{}/cluster?{}'.format(
            self.uri, parse.urlencode(arguments)),
            headers={'Key': self.uk}
        )

        if response.code == 200:
            return response.body.decode('utf-8')

        else:
            raise ValueError(response.body.decode('utf-8'))

    def cluster_list(self):
        arguments = {
            'method': 'clusters_list'
        }
        client = HTTPClient()
        response = client.fetch('{}/cluster?{}'.format(
            self.uri, parse.urlencode(arguments)),
            headers={'Key': self.uk}
        )

        if response.code == 200:
            return response.body.decode('utf-8')
        else:
            raise ValueError(response.body.decode('utf-8'))
