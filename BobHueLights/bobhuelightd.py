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
from threading import Thread
from BobHueLights.logger import init_logger
from BobHueLights.config import BobHueConfig
from BobHueLights.server import BobHueServer
from BobHueLights.server import BobHueRequestHandler
from BobHueLights.huelights import HueLights
from BobHueLights.hueupdate import HueUpdate
from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound, RequirementParseError

try:
    __version__ = get_distribution(__name__.split('.')[0]).version
except (DistributionNotFound, RequirementParseError):
    # package is not installed
    __version__ = 'dev'

# TODO: Create a config file and class to process it

def main():
    """
    The server needs to process the command arguments, open the logger
    and then start the daemon on the appropiate socket
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default=None,
                        help='location of configuration file')
    parser.add_argument('--debug', default=False,
                        action='store_true',
                        help='turn on debug logging information')
    parser.add_argument('--version', action='version',
                        version=__version__)
    args = parser.parse_args()

    # Initialise the logger
    init_logger('bobhuelightd.log', args.debug)
    logger = logging.getLogger('bobhuelightd')

    # Load the configuration file
    conf = BobHueConfig()
    conf.read_config(args.config)
    # Validate the conf fiela nd exit if bad
    if not conf.validate():
        exit(-1)

    # Initialise the lights
    bridge = conf.bridge_address
    user = conf.username
    lights = conf.lights
    HueLights().setup(lights)

    # Create a HueUpdate thread
    hue_updater = HueUpdate(bridge, user)
    if not hue_updater.connect():
        logger.critical('Could not connect to Hue Bridge')
        exit(-1)
    hue_thread = Thread(target=hue_updater.update)
    hue_thread.setDaemon(True)  # don't hang on exit
    hue_thread.start()

    # Start the server
    # TODO: Get the port from the config file (19333 is boblightserver)
    address = (socket.gethostname(), 19333)  # let the kernel assign a port
    server = BobHueServer(address, BobHueRequestHandler)
    ip, port = server.server_address  # what port was assigned?

    # Start the server in a thread
    server_thread = Thread(target=server.serve_forever)
    server_thread.setDaemon(True)  # don't hang on exit
    server_thread.start()
    server_thread.join()

    # Clean up
    hue_updater.shutdown()
    server.shutdown()
    logger.debug('done')
    server.socket.close()

    logger.info('Exiting...')

    return


# When running as a script we should call main
if __name__ == '__main__':
    main()
