from pylm.registry.clients.registry import request
from pylm.registry.clients import LogClient

from subprocess import Popen, PIPE
from concurrent.futures import ThreadPoolExecutor, as_completed

import argparse
import configparser
import traceback
import zmq
import sys

context = zmq.Context()


def parse_args():
    parser = argparse.ArgumentParser(description="Execute a PALM runner")
    parser.add_argument('--registry', help="URI of the registry", type=str, required=True)
    parser.add_argument('--cluster', help="sets the cluster key", type=str, required=True)
    parser.add_argument('--config', help="File with the node configuration", type=str, required=True)

    return parser.parse_args()


def message_hub(client):
    pull_socket = context.socket(zmq.PULL)
    pull_socket.bind("inproc://hub")

    while True:
        message = pull_socket.recv()
        message = message.decode('utf-8')
        message = message.strip('\n')
        if message:
            client.send(message)


def process_wrapper(commands):
    push_socket = context.socket(zmq.PUSH)
    push_socket.connect("inproc://hub")

    with Popen(commands, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            push_socket.send(line.encode('utf-8'))


def main():
    # If it does not provide all the args, it just dies.
    args = parse_args()

    # First step is to connect to the registry
    with open(args.config) as config_data:
        commands = request(args.registry, args.cluster, config_data.read())

    print(commands)
    if not commands:
        print('No command issued')
        return

    config = configparser.ConfigParser()
    config.read(args.config)
    processors = config.getint('DEFAULT', 'processors')
    client = LogClient(args.registry, args.cluster)

    futures = list()

    print('Serving logs ...')
    with ThreadPoolExecutor(max_workers=processors+1) as executor:
        for command in commands:
            futures.append(executor.submit(process_wrapper, command.split()))

        futures.append(executor.submit(message_hub, client))

        # Only gets here in case of error
        for i, future in enumerate(as_completed(futures)):
            try:
                result = future.result()
                if result:
                    print(result)
                else:
                    print('Task #{} completed'.format(i))

            except:
                print('{} generated an exception'.format(future))
                lines = traceback.format_exception(*sys.exc_info())
                for line in lines:
                    print(line)
