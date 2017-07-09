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
from BobHueLights.huelights import HueLights
from BobHueLights.hueupdate import HueUpdate
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__.split('.')[0]).version
except DistributionNotFound:
    # package is not installed
    __version__ = 'dev'

# TODO: Create a config file and class to process it
CONFIG = {
    'name' : 'MyHueBridge',
    'bridge' : '192.168.123.103',
    'username' : '-q7WH-udlI5-c0CGs71eUNrd-l9YxdGU6TmIOcEX',
    'lights' : {
        # Hue lightid : (Vtop, Vbot, Hleft, Hright)
        '1' : (50.0, 100.0, 80.0, 100.0),
        '2' : (50.0, 100.0, 0.0, 20.0),
        '7' : (0.0, 20.0, 0.0, 100.0)        
    }
}



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

    # Initialise the lights
    bridge = CONFIG['bridge']
    user = CONFIG['username']
    lights = CONFIG['lights']
    HueLights(lights)

    # Create a HueUpdate thread
    hue_updater = HueUpdate(bridge, user)
    if not hue_updater.connect():
        logger.critical('Could not connect to Hue Bridge')
        exit(-1)
    hue_thread = threading.Thread(target=hue_updater.update)
    hue_thread.setDaemon(True)  # don't hang on exit
    hue_thread.start()

    # Start the server
    # TODO: Get the port from the config file (19333 is boblightserver)
    address = (socket.gethostname(), 19333)  # let the kernel assign a port
    server = BobHueServer(address, BobHueRequestHandler)
    ip, port = server.server_address  # what port was assigned?

    # Start the server in a thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)  # don't hang on exit
    server_thread.start()
    server_thread.join()

    # Clean up
    server.shutdown()
    logger.debug('done')
    server.socket.close()

    logger.info('Exiting...')

    return


# When running as a script we should call main
if __name__ == '__main__':
    main()
