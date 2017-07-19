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


def init_logger(filename, debug, backups=2):
    """
    Initialise the logger
    Send INFO messages to console
    Send all messages to logfile
    Rotate the file after specified number of backups
    Defaults to 2 backups
    """
    loglevel = logging.DEBUG if debug else logging.INFO
    need_roll = os.path.isfile(filename)
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    file_fmt = logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)s] '
                                 '%(name)s %(funcName)s: %(message)s',
                                 datefmt='%Y%m%d %H:%M:%S')
    console_fmt = logging.Formatter('%(name)s: %(message)s')

    # Set console up for INFO only
    consoleh = logging.StreamHandler()
    consoleh.setLevel(logging.INFO)
    consoleh.setFormatter(console_fmt)

    # Create a rotating handler for the files with a max size of 250MB
    fileh = logging.handlers.RotatingFileHandler(filename,
                                                 maxBytes=100*1024*1024,
                                                 backupCount=backups)
    fileh.setLevel(loglevel)
    fileh.setFormatter(file_fmt)

    logger.addHandler(fileh)
    logger.addHandler(consoleh)

    # Rotate if there is an exisitng log file
    if need_roll:
        logger.debug('------------- Closing file and rotating --------------')
        fileh.doRollover()
