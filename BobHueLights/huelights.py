#!/usr/bin/env python3
"""
boblight_protocol
This module contains classes for handling the boblight protocol
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging

LIGHTS = {
    'left' : (20.0, 100.0, 0.0, 20.0),
    'right' : (20.0, 100.0, 80.0, 100.0),
    'top' : (0.0, 20.0, 0.0, 100.0)
}

class HueLights():
    """ Boblight protocol handler """
    def __init__(self):
        self.logger = logging.getLogger('HueLights')
        self.logger.debug('__init__')

    @property
    def count(self):
        """ Returns the count of lights configured on the system """
        # TODO: get this value from the config file
        self.logger.debug('Returning %d light', len(LIGHTS))
        return len(LIGHTS)

    @property
    def all_lights(self):
        """ Returns a dictionary of the lights """
        return LIGHTS

    def scanarea(self, light):
        """ returns the scan area for a specific light """
        lightdata = '{}: {!r}'.format(LIGHTS[light], LIGHTS[light].value)
        self.logger.debug('scanarea: %s'.format(lightdata))
        return lightdata
