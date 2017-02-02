from urllib import parse

from tornado.httpclient import HTTPClient

from pylm.registry.clients.registry import RegistryClient
from pylm.registry.clients.logs import LogClient


def new_admin_account(uri, master_key, admin_name, key=None):
    """
    Creates a new client account with the master key. The master key is part
    of the static configuration of the registry service.

    :param uri: URI of the registry service
    :param master_key: Master key for the registry service
    :param admin_name: Name of the admin account
    :param key: Key of the admin account
    :return: Key assigned to the admin account. It may be generated automatically
    """
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