#!/usr/bin/env python3
"""
hueboblightd
This module contains main daemon for the hueboblightd server
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import os
import logging
import argparse
import platform
import signal
import socket
from threading import Thread
from HueBobLightd.logger import init_logger
from HueBobLightd.config import BobHueConfig
from HueBobLightd.server import BobHueServer
from HueBobLightd.server import BobHueRequestHandler
from HueBobLightd.huelights import HueRequest, HueLight, HueUpdate
from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound, RequirementParseError

try:
    __version__ = get_distribution(__name__.split('.')[0]).version
except (DistributionNotFound, RequirementParseError):
    # package is not installed
    __version__ = 'dev'


class SignalCatcher:
    """ Catch the relevant signals and clean up the daemon """
    def __init__(self, server, light_updater):
        self.signint_hdlr = None
        self.sighup_hdlr = None
        self.server = server
        self.light_updater = light_updater

    def __enter__(self):
        """ Set up the handled signals """
        self.signint_hdlr = signal.signal(signal.SIGINT, self.signal_handler)
        if platform.system().lower() != 'windows':
            self.sighup_hdlr = signal.signal(signal.SIGHUP, self.signal_handler)

    def __exit__(self, type, value, traceback):
        """ Restore the handled signals """
        signal.signal(signal.SIGINT, self.signint_hdlr)
        signal.signal(signal.SIGHUP, self.sighup_hdlr)

    def signal_handler(self, signum, frame):
        """ Handler for the signals we are interested in """
        if signum == signal.SIGINT:
            logging.info('Caught SIGINT. Shutting down daemon')
            self.light_updater.shutdown()
            self.server.shutdown()
        elif signum == signal.SIGHUP:
            logging.info('Caught SIGHUP. Reloading config file')
            # TODO: Implement reloading of the config file and reinitialising lights


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
        logfile = '{}/hueboblightd.log'.format(args.logdir)
    else:
        logfile = '{}/hueboblightd.log'.format(os.getcwd())
    init_logger(logfile, backups=4, debug=args.debug)
    # init_logger('hueboblightd.log', True)
    logger = logging.getLogger('hueboblightd')
    logger.info('Started: version %s', __version__)

    # Load the configuration file
    conf = BobHueConfig()
    conf.read_config(args.config)
    # Validate the conf file and exit if bad
    if not conf.validate():
        exit(-1)

    # Initialise the bridge address and username
    HueRequest(conf.bridge_address, conf.username)

    lights = list()
    lights_conf = conf.get_parameter("lights")
    # Create a list of lights for the updater object
    for light in lights_conf:
        light_name = light['name']
        light_id = light['id']
        light_scan = (light['vscan']['top'], light['vscan']['bottom'],
                      light['hscan']['left'], light['hscan']['right'])
        light_gamut = light.get('gamut')
        hue = HueLight(light_name, light_id, *light_scan, light_gamut)
        logger.info('HueLight: %r', hue)
        lights.append(hue)

    # Create the light updater object
    hue_updater = HueUpdate(lights)

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

    with SignalCatcher(server, hue_updater):
        # Create a HueUpdate thread
        logger.info('Starting lights update thread')
        hue_thread = Thread(target=hue_updater.update_forever)
        hue_thread.setDaemon(True)  # don't hang on exit
        hue_thread.start()

        # Start the server in a thread
        logger.info('Starting server update thread: %r', server.server_address)
        server_thread = Thread(target=server.serve_forever)
        server_thread.setDaemon(True)  # don't hang on exit
        server_thread.start()

        # Go to sleep and wait for server thread to complete
        server_thread.join()
        hue_thread.join()

    server.socket.close()        # cleanup
    logger.info('Exiting...')

    return


# When running as a script we should call main
if __name__ == '__main__':
    main()
