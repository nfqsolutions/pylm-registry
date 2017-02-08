import configparser
import pickle
from collections import defaultdict, deque


class ConfigManager(object):
    """
    Class that manages the configuration of the cluster and prepares
    the information for the registry client that is running in each node.

    This is a first-shot implementation that may be a little complex, and it
    has been tested only for the most common cases.

    It still has to handle:

    * Multiple replicas of master servers.
    * Rules for exclusion
    * Cluster status management (if the cluster is OK to run)
    """
    def __init__(self, config_data, logger_func=print):
        self.requested_services = configparser.ConfigParser()
        self.requested_services.read_string(config_data)
        self.socket_assignment = defaultdict(list)
        self.socket_mapping = {}
        self.cluster_structure = {}
        self.configured_resources = {}
        self.highest_port_used = defaultdict(int)
        self.ready = False
        self.logger = logger_func

        # Compute the cluster structure
        for service in self.requested_services:
            if not service == 'DEFAULT':
                sockets = []
                commands = [self.requested_services[service]['Script']]

                for variable in self.requested_services[service]:
                    value = self.requested_services[service][variable]
                    if value.startswith('_'):
                        sockets.append(value)

                    if variable.startswith('--'):
                        # This is '{value} because {{ is the escaped {'
                        commands.append(' '.join([variable, '{{{}}}'.format(value)]))

                connections = [s.strip() for s in self.requested_services.get(
                    service, 'Connected', fallback='').split(',')
                ]
                if not connections[0]:
                    connections = []

                self.cluster_structure[service] = {
                    'sockets': sockets,
                    'commands': commands,
                    'connections': connections,
                    'role': self.requested_services.get(
                        service, 'Role', fallback='Master'),
                    'replicas': self.requested_services.getint(
                        service, 'Replicas', fallback=0),
                    'ready': False,
                    'order': 0,
                    }

        # Find dependencies from the socket connections.
        for name, service in self.cluster_structure.items():
            for socket in service['sockets']:
                self.socket_assignment[socket].append(name)

        # Determine the order in which the services have to be configured
        # The algorithm is simple now. If it has connections, it is configured
        # in a second round. This is important, because otherwise the
        # configuration of the cluster depends on how the cluster configuration
        # file was written
        order = deque()
        for server, structure in self.cluster_structure.items():
            if structure['connections']:
                # If it has at least one connection, last in the queue
                order.append(server)
            else:
                # If it has no connections, first in the queue
                order.appendleft(server)

        # And finally assign the order
        for service in order:
            self.cluster_structure[service]['order'] = order.index(service)

    def dump_status(self):
        return pickle.dumps((
            self.socket_mapping,
            self.configured_resources,
            self.highest_port_used,
            self.ready,
            ))

    def load_status(self, dump):
        if dump:
            (self.socket_mapping,
             self.configured_resources,
             self.highest_port_used,
             self.ready) = pickle.loads(dump)

    def process_resource(self, server_spec):
        """
        Process the server request and return the jobs to be run on the server.

        :param server_spec: String with the server spec
        :return:
        """
        server_config = configparser.ConfigParser()
        server_config.read_string(server_spec)

        # This configures the job to send to the server
        for i in range(server_config.getint('DEFAULT', 'processors')):
            processor_used = False
            # Configure the services with the established order
            for service, structure in sorted(self.cluster_structure.items(),
                                             key=lambda x: x[1]['order']):
                print(service)
                # Obtain the number of instances of a given service running
                service_instances = sum(
                    map(lambda x: x.startswith(service),
                        self.configured_resources)
                )
                if service_instances <= structure['replicas']:
                    # Here I need to allocate this available core.
                    ip = server_config.get('DEFAULT', 'ip')
                    if (server_config.getint('DEFAULT', 'ports_from') >
                            self.highest_port_used[ip]):
                        self.highest_port_used[ip] = server_config.getint(
                            'DEFAULT', 'ports_from')

                    # This is the complicated part, compute the necessary
                    # port numbers for the required sockets

                    for socket in structure['sockets']:
                        if socket not in self.socket_mapping:
                            self.socket_mapping[socket] = 'tcp://{}:{}'.format(
                                ip,
                                self.highest_port_used[ip]
                            )
                            self.highest_port_used[ip] += 1

                    resource_configuration = {
                        'commands': [
                            c.format(**self.socket_mapping)
                            for c in structure['commands']
                        ],
                        'node': ip
                    }

                    if structure['replicas']:
                        service_name = '{} {}'.format(service,
                                                      service_instances + 1)
                        self.configured_resources[service_name] = resource_configuration

                        intended_replicas = structure['replicas']
                        if intended_replicas == service_instances:
                            self.configured_resources[service_name]['ready'] = True
                    else:
                        self.configured_resources[service] = resource_configuration
                        self.configured_resources[service]['ready'] = True

                    processor_used = service
                    # Core configured, break the loop to configure the next
                    # core or to leave this server alone.
                    break

            if processor_used:
                self.logger("Resource used for {}".format(processor_used))
            else:
                self.logger("Resource {} core {} unused".format(
                    server_config.get('DEFAULT', 'Ip'),
                    i))

        # Return the configuration messages that belong to the server
        config_message = []

        if processor_used:
            for resource in self.configured_resources.values():
                if resource['node'] == server_config.get('DEFAULT', 'ip'):
                    config_message.append(' '.join(resource['commands']))

        print(config_message)
        return config_message
