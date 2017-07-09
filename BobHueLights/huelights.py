#!/usr/bin/env python3
"""
HueLights
This module contains a class for managing the lights associated with
the server, taking the updates from the client and ensuring the light's 
state is kept up to date.
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging


class HueLights():
    """ Boblight protocol handler """
    lights = dict()
    colors = dict()
    logger = None

    def __init__(self, huelights=dict()):
        if self.logger is None:
            self.logger = logging.getLogger('HueLights')
        self.logger.debug('__init__: %r', huelights)
        for light, scanval in huelights.items():
            # Only add lights if they have not already been defined
            if self.lights.get(light) is None:
                self.lights[light] = scanval
            if self.colors.get(light) is None:
                self.colors[light] = (0.0, 0.0, 0.0)

    @property
    def count(self):
        """ Returns the count of lights configured on the system """
        # TODO: get this value from the config file
        self.logger.debug('Returning %d light', len(self.lights))
        return len(self.lights)

    @property
    def all_lights(self):
        """ Returns a dictionary of the lights scaninfo """
        return self.lights

    @property
    def all_colors(self):
        """ Returns a dictionary of the lights colors """
        return self.colors

    def get_light_color(self, name):
        """ Returns the current colour of a light """
        return self.colors.get(name)

    def set_light_color(self, name, rgb):
        """ Set a light to a given colour """
        self.colors[name] = rgb
