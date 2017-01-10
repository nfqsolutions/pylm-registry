import io
import configparser


class ClusterManager(object):
    def __init__(self, config_data):
        self.requested_services = configparser.ConfigParser()
        self.requested_services.read_string(config_data)
        self.allocated_services = []

    def process_request(self, server_spec):
        """
        Process the server request and return the jobs to be run on the server.

        :param server_spec:
        :return:
        """
        server_config = configparser.ConfigParser()
        buffer = io.StringIO(server_spec)
        server_config.read(buffer)

        # This configures the job to send to the server
        for service in self.requested_services:
            if service not in self.allocated_services:
                print(service)


