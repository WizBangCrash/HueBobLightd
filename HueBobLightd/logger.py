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


def init_logger(filename, debug):
    """
    Initialise the logger
    Send INFO messages to console
    Send all messages to logfile
    Rotate the file after specified number of backups
    """
    loglevel = logging.DEBUG if debug else logging.INFO
    backups = 2
    need_roll = os.path.isfile(filename)
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    file_fmt = logging.Formatter('%(asctime)s.%(msecs)d [%(levelname)s] '
                                 '%(name)s %(funcName)s: %(message)s',
                                 datefmt='%Y%m%d %H:%M:%S')
    console_fmt = logging.Formatter('%(name)s: %(message)s')

    # Set console up for INFO only
    consoleh = logging.StreamHandler()
    # TODO: consoleh.setLevel(logging.INFO)
    consoleh.setLevel(logging.INFO)
    consoleh.setFormatter(console_fmt)

    # Create a rotating handler for the files
    fileh = logging.handlers.RotatingFileHandler(filename, backupCount=backups)
    fileh.setLevel(loglevel)
    fileh.setFormatter(file_fmt)

    logger.addHandler(fileh)
    logger.addHandler(consoleh)

    # Rotate if there is an exisitng log file
    if need_roll:
        logger.debug('------------- Closing file and rotating --------------')
        fileh.doRollover()