import argparse


def main():
    parser = argparse.ArgumentParser(description="Execute a PALM runner")
    parser.add_argument('--cluster', help="sets the cluster key", type=str, required=True)

    args = parser.parse_args()

    print('hello')