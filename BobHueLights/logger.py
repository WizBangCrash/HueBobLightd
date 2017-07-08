#!/usr/bin/env python3
"""
bobhuelightd
This module contains main daemon for the bobhuelightd server
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import os
import logging
import logging.handlers


def init_logger(filename):
    """
    Initialise the logger
    Send INFO messages to console
    Send all messages to flogfile
    Rotate the file after specified number of backups
    """
    # TODO: Get logdir, logfile & loglevel from the config file
    logfile = '{}/{}'.format(os.getcwd(), filename)
    backups = 2
    need_roll = os.path.isfile(logfile)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter('%(asctime)s [%(levelname)s] '
                                 '%(name)s %(funcName)s: %(message)s',
                                 datefmt='%Y%m%d %H:%M:%S')
    console_fmt = logging.Formatter('%(name)s: %(message)s')

    # Set console up for INFO only
    consoleh = logging.StreamHandler()
    # TODO: consoleh.setLevel(logging.INFO)
    consoleh.setLevel(logging.DEBUG)
    consoleh.setFormatter(console_fmt)

    # Create a rotating handler for the files
    fileh = logging.handlers.RotatingFileHandler(logfile, backupCount=backups)
    fileh.setLevel(logging.DEBUG)
    fileh.setFormatter(file_fmt)

    logger.addHandler(fileh)
    logger.addHandler(consoleh)

    # Rotate if there is an exisitng log file
    if need_roll:
        logger.debug('------------- Closing file and rotating --------------')
        fileh.doRollover()
