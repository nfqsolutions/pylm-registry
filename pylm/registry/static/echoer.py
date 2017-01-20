"""
Echoer for testing the subprocess launch and the logs without using
actual servers.
"""

import sys
import time
import logging


logger = logging.getLogger('echoer')
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

counter = 0

while True:
    time.sleep(1)
    counter += 1
    logger.info('Hi counter #{}\n'.format(counter))
    
