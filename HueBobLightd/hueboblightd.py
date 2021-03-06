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
from threading import Thread, Event
from HueBobLightd.logger import init_logger
from HueBobLightd.config import BobHueConfig
from HueBobLightd.server import BobHueServer
from HueBobLightd.server import BobHueRequestHandler
from HueBobLightd.lightupdate import LightsUpdater
from HueBobLightd.huelights import HueLight, BridgeAddress
from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound, RequirementParseError

try:
    __version__ = get_distribution(__name__.split('.')[0]).version
except (DistributionNotFound, RequirementParseError):
    # package is not installed
    __version__ = 'dev'


class BoblightDaemon():
    """
    Class for managing the server daemon
    Implemented with contextlib to wrapthe signal handlers
    """
    logger = None

    def __init__(self, server, updater):
        if type(self).logger is None:
            type(self).logger = logging.getLogger(type(self).__name__)
        self.event = Event()
        self.handlers = dict()
        self.signal = None
        self.server_thread = None
        self.updater_thread = None
        self.server = server
        self.updater = updater
        self.lights = list()

    def __enter__(self):
        """ Register signal handlers """
        self.handlers['SIGINT'] = signal.signal(signal.SIGINT, self.signal_handler)
        self.handlers['SIGTERM'] = signal.signal(signal.SIGTERM, self.signal_handler)
        if platform.system().lower() != 'windows':
            self.handlers['SIGHUP'] = signal.signal(signal.SIGHUP, self.signal_handler)
            self.handlers['SIGUSR1'] = signal.signal(signal.SIGUSR1, self.signal_handler)
        return self

    def __exit__(self, extype, exvalue, extraceback):
        """ Reset signal handlers """
        signal.signal(signal.SIGINT, self.handlers['SIGINT'])
        signal.signal(signal.SIGTERM, self.handlers['SIGTERM'])
        if platform.system().lower() != 'windows':
            signal.signal(signal.SIGHUP, self.handlers['SIGHUP'])
            signal.signal(signal.SIGHUP, self.handlers['SIGUSR1'])

    def signal_handler(self, signum, frame):
        """ Save the signal for the wait method """
        #pylint: disable=W0613
        self.logger.info('Caught signal: %r', signum)
        self.signal = signum
        if signum == signal.SIGUSR1:
            """
            If we get a SIGUSR1 signal then switch the log level
            in/out of DEBUG mode
            """
            # self.logger.info('Log level was: %r', self.logger.getEffectiveLevel())
            if self.logger.getEffectiveLevel() == logging.DEBUG:
                logging.getLogger().setLevel(logging.INFO)
            else:
                logging.getLogger().setLevel(logging.DEBUG)
        else:
            self.event.set()

    def create_lights(self, config):
        """ Create a list of lights from the configuration file data """
        # Retrieve the light tranition time
        transition = config.get_parameter('transitionTime', 3)
        # Create lights for all bridges
        for bridge in config.get_parameter('bridges'):
            bridge_addr = BridgeAddress(bridge['address'], bridge['username'])
            # Create a list of lights on the bridge
            for light in bridge.get('lights'):
                new_light = {
                    'address' : bridge_addr,
                    'name' : light['name'],
                    'hue_id' : light['id'],
                    'brightness' : light.get('brightness', 150),
                    'gamut' : light.get('gamut', ''),
                    'scanarea' : (
                        light['vscan']['top'],
                        light['vscan']['bottom'],
                        light['hscan']['left'],
                        light['hscan']['right']
                    ),
                    'transition' : light.get('transitionTime', transition)
                }
                self.lights.append(new_light)

    def start_server(self):
        """ Create and start the server thread """
        if self.server_thread is None:
            self.logger.info('Starting Server thread %r', self.server.server_address)
            self.server_thread = Thread(target=self.server.serve_forever)
            self.server_thread.setDaemon(True)  # don't hang on exit
            self.server_thread.start()
        else:
            self.logger.debug('Server thread already running')

    def stop_server(self):
        """ Stop the server thread and wait for it to exit """
        self.logger.info('Stopping Server thread')
        self.server.shutdown()
        self.server_thread.join()
        self.server_thread = None
        self.logger.debug('Closing Server socket')
        self.server.socket.close()

    def start_updater(self):
        """ Create and start the updater thread """
        if self.updater_thread is None:
            self.logger.info('Starting Updater thread')
            self.updater_thread = Thread(target=self.updater.update_forever)
            self.updater_thread.setDaemon(True)  # don't hang on exit
            self.updater_thread.start()
        else:
            self.logger.debug('Updater thread already running')

    def stop_updater(self):
        """ Stop the updater thread and wait for it to exit """
        self.logger.info('Stopping Updater thread')
        self.updater.shutdown()
        self.updater_thread.join()
        self.updater_thread = None

    def wait(self):
        """ Waits for a signal to be sent to the daemon """
        self.event.wait()
        self.event.clear()
        # Reset signal flag
        sig = self.signal
        self.signal = None
        # Returns true if the signal was a SIGHUP
        return sig == signal.SIGHUP

#pylint: disable=R0912
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
                        help='IPv4 socket_addr of boblightd server')
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
        logger.info('Exiting due to config file issues')
        exit(-1)

    # Create the light updater object
    updater = LightsUpdater()

    # Create the server
    if args.server:
        socket_addr = (args.server, conf.server_port)
    elif conf.server_address:
        socket_addr = (conf.server_address, conf.server_port)
    else:
        socket_addr = (socket.gethostname(), conf.server_port)  # let the kernel assign a port
    # TODO: Figure out how to correctly get the hostname on iMac and Synology
    logger.info('gethostname() = %r', socket_addr)
    server = BobHueServer(socket_addr, BobHueRequestHandler)

    with BoblightDaemon(server, updater) as bld:
        try:
            while True:
                # Retrieve the auto off value and turn into seconds
                updater.auto_off_delay = conf.get_parameter('autoOff', False) * 60
                # Create lights for all bridges
                bld.lights.clear()
                bld.create_lights(conf)
                for light in bld.lights:
                    try:
                        hue_light = HueLight(**light)
                    except ValueError:
                        logger.exception('Failed to initialise light: %r', light)
                    else:
                        bld.updater.add(hue_light)
                        logger.info('Added light: %r', light)

                # Store the update object as data in the server for the requesthandler
                bld.server.data = bld.updater
                # Start the updater thread
                logger.info('Starting lights update thread:')
                bld.start_updater()
                # Start the server thread
                logger.info('Starting server update thread: %r',
                            socket_addr)
                bld.start_server()

                # Wait until a signal occurs
                if bld.wait():
                    # If true then we need to restart
                    if args.server is None and conf.server_address:
                        new_socket_addr = (conf.server_address, conf.server_port)
                        if new_socket_addr != socket_addr:
                            # Only restart the server if it's socket_addr has changed
                            bld.stop_server()
                            del server
                            socket_addr = new_socket_addr
                            server = BobHueServer(socket_addr, BobHueRequestHandler)
                    # Shutdown the updater before we rebuild the lights
                    bld.stop_updater()
                else:
                    # If false we need to exit
                    bld.stop_server()
                    bld.stop_updater()
                    break

                # Re-read the config
                conf.merge_config(args.config)
                if not conf.validate():
                    logger.critical('Invalid configuration file')
                    break

        #pylint: disable=W0702
        except:
            logger.exception('Something bad happened :-(')

    logger.info('Exiting...')

    return


# When running as a script we should call main
if __name__ == '__main__':
    main()
