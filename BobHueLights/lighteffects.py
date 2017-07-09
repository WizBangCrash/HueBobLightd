#!/usr/bin/env python3
"""
lighteffects
This module contains test client for the bobhueserverd
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
import argparse
import socket
from BobHueLights.logger import init_logger
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__.split('.')[0]).version
except DistributionNotFound:
    # package is not installed
    __version__ = 'dev'


def main():
    """
    The client sends messages that the AppleTV4 would send
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        version=__version__)
    args = parser.parse_args()

    # Initialise the logger
    init_logger('lighteffects.log')
    logger = logging.getLogger('LightEffects')

    address = (socket.gethostname(), 19333)
    # address = ('192.168.123.192', 19333)
    logger.info('Server on %s', address)

    # Connect to the server
    logger.info('creating socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info('connecting to server')
    s.connect(address)

    # Send the data
    message = b'hello\n'
    logger.info('sending data: %r', message)
    len_sent = s.send(message)

    # Receive a response
    logger.info('waiting for response')
    response = s.recv(1000)
    logger.info('response from server: %r', response)
    # exit(0)

    message = b'ping\n'
    logger.info('sending data: %r', message)
    len_sent = s.send(message)

    # Receive a response
    logger.info('waiting for response')
    response = s.recv(1000)
    logger.info('response from server: %r', response)

    message = b'get version\n'
    logger.info('sending data: %r', message)
    len_sent = s.send(message)

    # Receive a response
    logger.info('waiting for response')
    response = s.recv(1000)
    logger.info('response from server: %r', response)

    message = b'get lights\n'
    logger.info('sending data: %r', message)
    len_sent = s.send(message)

    # Receive a response
    logger.info('waiting for response')
    response = s.recv(1000).decode()
    logger.info('response from server: %r', response)

    message = b'set light 1 rgb 0.000000 1.000000 0.000000\n'
    logger.info('sending data: %r', message)
    len_sent = s.send(message)

    message = b'set light 2 rgb 1.000000 0.000000 0.000000\n'
    logger.info('sending data: %r', message)
    len_sent = s.send(message)

    message = b'set light 7 rgb 0.000000 0.000000 1.000000\n'
    logger.info('sending data: %r', message)
    len_sent = s.send(message)

    # Clean up
    logger.info('closing socket')
    s.close()
    logger.info('done')

    logging.info('Exiting...')

    return


# When running as a script we should call main
if __name__ == '__main__':
    main()
