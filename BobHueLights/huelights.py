#!/usr/bin/env python3
"""
boblight_protocol
This module contains classes for handling the boblight protocol
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging

class HueLights():
    """ Boblight protocol handler """
    def __init__(self):
        self.logger = logging.getLogger('HueLights')
        self.logger.debug('__init__')

    @property
    def count(self):
        """ Returns the count of lights configured on the system """
        # TODO: get this value from the config file
        self.logger.debug('Returning 1 light')
        return 1

    def scanarea(self, light):
        """ returns the scan area for a specific light """
        self.logger.debug('Returning: 0.0, 100.0, 0.0, 100.0')
        return (0.0, 100.0, 0.0, 100.0)
