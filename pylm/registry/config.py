import configparser
import os

configuration = configparser.ConfigParser()
configuration.read(os.environ['PYLM_REGISTRY_CONFIG'])
