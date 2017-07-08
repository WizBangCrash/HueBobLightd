#!/usr/bin/env python3
"""
bobhuelightd
This module contains main daemon for the bobhuelightd server
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
import argparse
import socket
import socketserver
import threading
from BobHueLights.logger import init_logger
from BobHueLights.server import BobHueServer
from BobHueLights.server import BobHueRequestHandler
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__.split('.')[0]).version
except DistributionNotFound:
    # package is not installed
    __version__ = 'dev'

# TODO: Create a config file and class to process it

def main():
    """x
    The server needs to process the command arguments, open the logger
    and then start the daemon on the appropiate socket
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        version=__version__)
    args = parser.parse_args()

    # Initialise the logger
    init_logger('bobhuelightd.log')
    logger = logging.getLogger('bobhuelightd')

    # Start the server
    # TODO: Get the port from the config file (19333 is boblightserver)
    address = (socket.gethostname(), 19333)  # let the kernel assign a port
    server = BobHueServer(address, BobHueRequestHandler)
    ip, port = server.server_address  # what port was assigned?

    # Start the server in a thread
    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True)  # don't hang on exit
    t.start()
    t.join()

    # logger = logging.getLogger('client')
    # logger.info('Server on %s:%s', ip, port)

    # # Connect to the server
    # logger.debug('creating socket')
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # logger.debug('connecting to server')
    # s.connect((ip, port))

    # # Send the data
    # message = 'Hello, world'.encode()
    # logger.debug('sending data: %r', message)
    # len_sent = s.send(message)

    # # Receive a response
    # logger.debug('waiting for response')
    # response = s.recv(len_sent)
    # logger.debug('response from server: %r', response)

    # Clean up
    server.shutdown()
    # logger.debug('closing socket')
    # s.close()
    logger.debug('done')
    server.socket.close()

    logger.info('Exiting...')

    return


# When running as a script we should call main
if __name__ == '__main__':
    main()
