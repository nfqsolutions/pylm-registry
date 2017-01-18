import json
from urllib import parse

from tornado.httpclient import HTTPClient


class AdminClient(object):
    """
    Admin client to manage users

    :param uri: Address of the registry service
    :param admin_key: User key for this administrator
    """
    def __init__(self, uri, admin_key):
        self.uri = uri
        self.ak = admin_key

    def new_user(self, name, data={}, key=''):
        """
        Set a new user foor the service

        :param name: Name of the new user
        :param data: Dictionary with additional user data
        :param key: Key assigned to the user
        :return: Key actually assigned to the user
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
        """
        Get the list with all the users
        """
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

    def view_user_list(self):
        """
        Display the user list
        """
        user_list = self.user_list()
        if user_list:
            print(*(user_list[0].keys()))
            for user in user_list:
                print(*user.values())

    def delete_user(self, key):
        """
        Delete a user given its key
        """
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