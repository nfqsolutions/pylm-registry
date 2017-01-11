import configparser
from collections import defaultdict


class ClusterManager(object):
    def __init__(self, config_data):
        self.requested_services = configparser.ConfigParser()
        self.requested_services.read_string(config_data)
        self.socket_assignment = defaultdict(list)
        self.cluster_structure = {}
        self.configured_resources = {}
        self.ready = False

        # Compute the cluster structure
        for service in self.requested_services:
            if not service == 'DEFAULT':
                sockets = []
                commands = [
                    'python3 {}'.format(
                        self.requested_services[service]['Script']
                    )
                ]

                for variable in self.requested_services[service]:
                    value = self.requested_services[service][variable]
                    if value.startswith('{'):
                        sockets.append(value)

                    if variable.startswith('--'):
                        commands.append(' '.join([variable, value]))

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
                        service, 'Replicas', fallback=0)
                    }

        # Find dependencies from the socket connections.
        for name, service in self.cluster_structure.items():
            for socket in service['sockets']:
                self.socket_assignment[socket].append(name)

        print(self.cluster_structure)
        print(self.socket_assignment)

    def process_resource(self, server_spec):
        """
        Process the server request and return the jobs to be run on the server.

        :param server_spec:
        :return:
        """
        server_config = configparser.ConfigParser()
        server_config.read_string(server_spec)

        # This configures the job to send to the server
        for i in range(server_config.getint('DEFAULT', 'processors')):
            processor_used = False
            # Find a suitable service
            for service in self.cluster_structure:
                # Obtain the number of instances of a given service runniing
                service_instances = sum(
                    map(lambda x: x.startswith(service),
                        self.configured_resources)
                )
                if service_instances <= self.cluster_structure[service]['replicas']:
                    if self.cluster_structure[service]['replicas']:
                        self.configured_resources['{} {}'.format(
                            service,
                            service_instances+1)] = None
                    else:
                        self.configured_resources[service] = None
                        print('Configuring...')

                    processor_used = service

            if processor_used:
                print("Resource used for {}".format(processor_used))
            else:
                print("Resource {} core {} unused".format(
                    server_config.get('DEFAULT', 'Ip'),
                    i))

        print(self.configured_resources)