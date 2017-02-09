from pylm.registry.clients.registry import request
from pylm.registry.clients import LogClient
from pylm.registry.messages.registry_pb2 import LogMessages

from subprocess import Popen, PIPE
from concurrent.futures import ThreadPoolExecutor, as_completed

import argparse
import configparser
import traceback
import time
import zmq
import sys

context = zmq.Context()

# Global messages store.
messages = []

# Default config data
default_config = """
[DEFAULT]
Name = My Worker
Ip = 127.0.0.1
Processors = 1
Ports_from = 5555
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Execute a PALM runner")
    parser.add_argument('--registry', help="URI of the registry", type=str,
                        required=True)
    parser.add_argument('--cluster', help="sets the cluster key", type=str,
                        required=True)
    parser.add_argument('--config', help="File with the node configuration, "
                                         "if not provided, it assumes you "
                                         "want to use only one core to run "
                                         "one process",
                        default='',
                        type=str)

    return parser.parse_args()


def message_hub():
    pull_socket = context.socket(zmq.PULL)
    pull_socket.bind("inproc://hub")

    while True:
        message = pull_socket.recv()
        message = message.decode('utf-8')
        message = message.strip('\n')
        if message:
            messages.append(message)


def message_pusher(client):
    while True:
        time.sleep(1)
        if len(messages) > 0:
            print('Sent {} log lines'.format(len(messages)))
            buffer = LogMessages()
            buffer.messages.extend(messages)
            client.send(buffer.SerializeToString())

            # This clears the list with style
            del messages[:]


def process_wrapper(commands):
    push_socket = context.socket(zmq.PUSH)
    push_socket.connect("inproc://hub")

    with Popen(commands, stdout=PIPE, universal_newlines=True) as p:
        for line in p.stdout:
            push_socket.send(line.encode('utf-8'))


def main():
    # If it does not provide all the args, it just dies.
    args = parse_args()

    if args.config:
        # First step is to connect to the registry
        with open(args.config) as config_data:
            commands = request(args.registry, args.cluster, config_data.read())

    else:
        commands = request(args.registry, args.cluster, default_config)

    print(commands)
    if not commands:
        print('No command issued')
        return

    processors = 1
    if args.config:
        config = configparser.ConfigParser()
        config.read(args.config)
        processors = config.getint('DEFAULT', 'processors')

    client = LogClient(args.registry, args.cluster)

    futures = list()

    print('Serving logs ...')
    with ThreadPoolExecutor(max_workers=processors+2) as executor:
        for command in commands:
            futures.append(executor.submit(process_wrapper, command.split()))

        futures.append(executor.submit(message_hub))
        futures.append(executor.submit(message_pusher, client))

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
