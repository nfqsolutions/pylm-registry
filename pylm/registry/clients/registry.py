import json
from urllib import parse

from tornado.httpclient import HTTPClient


class RegistryClient(object):
    """
    Registry client to manage clusters.

    :param uri: Address of the registry service
    :param user_key: This user's key for the service
    """
    def __init__(self, uri, user_key):
        self.uri = uri
        self.uk = user_key

    def set_cluster(self, config_file, key=None):
        """
        Load a config file to the registry and make it a cluster

        :param config_file: Path to the config file to be loaded
        :param key: Key that identifies the cluster
        :return: Key that identifies the cluster. It can be generated if it is
            not given as a parameter. Use only while debugging.
        """
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
        """
        Get the list of all the clusters created by this user

        :return: A dictionary with all the clusters
        """
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
        """
        Pretty print the cluster list available
        """
        clusters = self.cluster_list()
        if clusters:
            print('Key', 'when', sep='\t')
            for key, data in clusters.items():
                if 'when' not in data:
                    print(key, '***', sep='\t')
                else:
                    print(key, data['when'], sep='\t')

    def view_cluster(self, key):
        """
        Pretty print the configuration of a single cluster

        :param key: The cluster key
        """
        clusters = self.cluster_list()
        if clusters:
            if key in clusters:
                data = clusters[key]
                print('key: ', key)
                print('Configuration')
                for cluster_data in data.values():
                    print(cluster_data)

                print('=========== ')
                print(' ')

            else:
                raise ValueError('Cluster not found')

    def request(self, cluster_key, configuration):
        """
        As an available resource, pass the configuration to the registry
        and get the commands that have to be run.

        :param cluster_key: Key of the cluster the resource wants to connect to
        :param configuration: String with the configuration of the resource
        :return: List with the commands that have to be run.
        """
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
        """
        Get the present status of the cluster

        :param cluster_key: Key that identifies the cluster
        :return: The status of the cluster
        """
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
        """
        Reset the status of a cluster. This means that all the temporary
        information about which resource request is forgotten. This may
        leave configured resources not properly configured, so handle with
        care.

        :param cluster_key:
        :return: Key of the cluster being reset
        """
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


def request(uri, cluster_key, configuration):
    """
    As an available resource, pass the configuration to the registry
    and get the commands that have to be run.

    :param uri: Address of the Registry
    :param cluster_key: Key of the cluster the resource wants to connect to
    :param configuration: String with the configuration of the resource
    :return: List with the commands that have to be run.
    """
    arguments = {
        'method': 'node_config',
        'cluster': cluster_key,
        'node': configuration
    }
    client = HTTPClient()
    response = client.fetch('{}/cluster?{}'.format(
        uri, parse.urlencode(arguments))
    )

    if response.code == 200:
        return json.loads(response.body.decode('utf-8'))
    else:
        raise ValueError(response.body.decode('utf-8'))
