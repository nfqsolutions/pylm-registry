from tornado.httpclient import HTTPClient
from urllib import parse
import json


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

    def new_user(self, name, data={}, key=''):
        """
        Set a new user for

        :param name:
        :param data:
        :param key:
        :return:
        """
        arguments = {
            'method': 'new_user',
            'name': name,
            'data': json.dumps(data),
            'key': key
        }

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
            return json.loads(response.body.decode('utf-8'))

        else:
            raise ValueError(response.body.decode('utf-8'))

    def delete_user(self, key):
        arguments = {
            'method': 'delete_user',
            'key': key
        }

        client = HTTPClient()
        response = client.fetch('{}/admin?{}'.format(
            self.uri, parse.urlencode(arguments)),
            headers={'Key': self.ak}
        )

        if response.code == 200:
            return response.body.decode('utf-8')

        else:
            raise ValueError(response.body.decode('utf-8'))

    def view_user_list(self):
        user_list = self.user_list()
        if user_list:
            print(*(user_list[0].keys()))
            for user in user_list:
                print(*user.values())


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
            return json.loads(response.body.decode('utf-8'))
        else:
            raise ValueError(response.body.decode('utf-8'))

    def view_cluster_list(self):
        clusters = self.cluster_list()
        if clusters:
            print('key', *(clusters.keys()))
            for cluster_data in clusters.values():
                print(*cluster_data.values())

    def request(self, cluster_key, configuration):
        arguments = {
            'method': 'node_config',
            'cluster': cluster_key,
            'node': configuration
        }
        client = HTTPClient()
        response = client.fetch('{}/cluster?{}'.format(
            self.uri, parse.urlencode(arguments)),
            headers={'Key': self.uk}
        )

        if response.code == 200:
            return json.loads(response.body.decode('utf-8'))
        else:
            raise ValueError(response.body.decode('utf-8'))

    def cluster_status(self, cluster_key):
        arguments = {
            'method': 'cluster_status',
            'cluster': cluster_key
        }
        client = HTTPClient()
        response = client.fetch('{}/cluster?{}'.format(
            self.uri, parse.urlencode(arguments)),
            headers={'Key': self.uk}
        )

        if response.code == 200:
            if response.body:
                return json.loads(response.body.decode('utf-8'))
            else:
                return "Empty"
        else:
            raise ValueError(response.body.decode('utf-8'))

    def cluster_reset(self, cluster_key):
        arguments = {
            'method': 'cluster_reset',
            'cluster': cluster_key
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