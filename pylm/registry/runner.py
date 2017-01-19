from pylm.registry.clients.registry import request
from pylm.registry.clients import LogClient

import subprocess
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Execute a PALM runner")
    parser.add_argument('--registry', help="URI of the registry", type=str, required=True)
    parser.add_argument('--cluster', help="sets the cluster key", type=str, required=True)
    parser.add_argument('--config', help="File with the node configuration", type=str, required=True)

    return parser.parse_args()


def main():
    # If it does not provide all the args, it just dies.
    args = parse_args()

    # First step is to connect to the registry
    with open(args.config) as config_data:
        commands = request(args.registry, args.cluster, config_data.read())

    print(commands)