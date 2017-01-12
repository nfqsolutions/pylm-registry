import configparser
from collections import defaultdict


class ClusterManager(object):
    def __init__(self, config_data):
        self.requested_services = configparser.ConfigParser()
        self.requested_services.read_string(config_data)
        self.socket_assignment = defaultdict(list)
        self.socket_mapping = {}
        self.cluster_structure = {}
        self.configured_resources = {}
        self.highest_port_used = defaultdict(int)
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
                    if value.startswith('_'):
                        sockets.append(value)

                    if variable.startswith('--'):
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
                    'ready': False
                    }

        # Find dependencies from the socket connections.
        for name, service in self.cluster_structure.items():
            for socket in service['sockets']:
                self.socket_assignment[socket].append(name)

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
                # Obtain the number of instances of a given service running
                service_instances = sum(
                    map(lambda x: x.startswith(service),
                        self.configured_resources)
                )
                if service_instances <= self.cluster_structure[service]['replicas']:
                    # Here I need to allocate this available core.
                    ip = server_config.get('DEFAULT', 'ip')
                    if server_config.getint('DEFAULT', 'ports_from') > self.highest_port_used[ip]:
                        self.highest_port_used[ip] = server_config.getint('DEFAULT', 'ports_from')

                    # This is the complicated part, compute the necessary port numbers
                    # for the required sockets

                    for socket in self.cluster_structure[service]['sockets']:
                        if socket not in self.socket_mapping:
                            self.socket_mapping[socket] = 'tcp://{}:{}'.format(
                                ip,
                                self.highest_port_used[ip]
                            )
                            self.highest_port_used[ip] += 1

                    resource_configuration = {
                        'commands': [
                            c.format(**self.socket_mapping) for c in self.cluster_structure[service]['commands']
                        ],
                        'node': ip
                    }

                    if self.cluster_structure[service]['replicas']:
                        self.configured_resources['{} {}'.format(
                            service,
                            service_instances+1)] = resource_configuration

                        intended_replicas = self.cluster_structure[service]['replicas']
                        if intended_replicas == service_instances:
                            self.cluster_structure[service]['ready'] = True
                    else:
                        self.configured_resources[service] = resource_configuration
                        self.cluster_structure[service]['ready'] = True

                    processor_used = service
                    # Core configured, break the loop to configure the next
                    # core or to leave this server alone.
                    break

            if processor_used:
                print("Resource used for {}".format(processor_used))
            else:
                print("Resource {} core {} unused".format(
                    server_config.get('DEFAULT', 'Ip'),
                    i))

        # Check which
        config_message = []

        for resource in self.configured_resources.values():
            if resource['node'] == server_config.get('DEFAULT', 'ip'):
                config_message.append(' '.join(resource['commands']))

        return config_message
