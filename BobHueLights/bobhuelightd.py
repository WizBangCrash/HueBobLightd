#!/usr/bin/env python3
"""
bobhuelightd
This module contains main daemon for the bobhuelightd server
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import os
import logging
import argparse
import socket
from threading import Thread
from BobHueLights.logger import init_logger
from BobHueLights.config import BobHueConfig
from BobHueLights.server import BobHueServer
from BobHueLights.server import BobHueRequestHandler
from BobHueLights.huelights import HueRequest, HueLight, HueUpdate
from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound, RequirementParseError

try:
    __version__ = get_distribution(__name__.split('.')[0]).version
except (DistributionNotFound, RequirementParseError):
    # package is not installed
    __version__ = 'dev'


def main():
    """
    The server needs to process the command arguments, open the logger
    and then start the daemon on the appropiate socket
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default=None,
                        help='location of configuration file')
    parser.add_argument('--logdir', type=str, default=None,
                        help='location of log files')
    parser.add_argument('--server', type=str, default=None,
                        help='IPv4 address of boblightd server')
    parser.add_argument('--debug', default=False,
                        action='store_true',
                        help='turn on debug logging information')
    parser.add_argument('--version', action='version',
                        version=__version__)
    args = parser.parse_args()

    # Initialise the logger
    if args.logdir:
        logfile = '{}/bobhuelightd.log'.format(args.logdir)
    else:
        logfile = '{}/bobhuelightd.log'.format(os.getcwd())
    init_logger(logfile, args.debug)
    # init_logger('bobhuelightd.log', True)
    logger = logging.getLogger('bobhuelightd')
    logger.info('Started: version %s', __version__)

    # Load the configuration file
    conf = BobHueConfig()
    conf.read_config(args.config)
    # Validate the conf file and exit if bad
    if not conf.validate():
        exit(-1)

    # Initialise the lights
    HueRequest(conf.bridge_address, conf.username)
    if not HueRequest.connect():
        logger.error('Unable to connect to bridge at address "%s"',
                     conf.bridge_address)
        exit(-1)

    lights = list()
    lights_conf = conf.get_parameter("lights")
    for light in lights_conf:
        light_name = light['name']
        light_id = light['id']
        light_scan = (light['vscan']['top'], light['vscan']['bottom'],
                      light['hscan']['left'], light['hscan']['right'])
        light_gamut = light.get('gamut')
        lights.append(HueLight(light_name, light_id, *light_scan, light_gamut))

    for light in lights:
        logger.info('HueLight: %r', light)

    # Create a HueUpdate thread
    # TODO: Remove HueUpdate and just create a function in this
    #       file to update the lights
    logger.info('Starting lights update thread')
    hue_updater = HueUpdate(lights)
    if not hue_updater.connect():
        logger.critical('Could not connect to Hue Bridge')
        exit(-1)
    hue_thread = Thread(target=hue_updater.update_forever)
    hue_thread.setDaemon(True)  # don't hang on exit
    hue_thread.start()

    # Create the server
    if args.server:
        address = (args.server, conf.server_port)
    elif conf.server_address:
        address = (conf.server_address, conf.server_port)
    else:
        address = (socket.gethostname(), conf.server_port)  # let the kernel assign a port
    server = BobHueServer(address, BobHueRequestHandler)
    # Store the HueLight array as data in the server for the requesthandler
    server.data = lights

    # Start the server in a thread
    logger.info('Starting server update thread: %r', server.server_address)
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
