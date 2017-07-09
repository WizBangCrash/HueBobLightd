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
import copy
from threading import Lock

"""
Create a HueLight class
Members:
    red, green, blue
    use: on / off
Methods:
    turn_on
    turn_off
    in_use
    update: send request to bridge
This may be a better way of representing the light a
"""

class HueLights():
    """ Boblight protocol handler """
    logger = None
    lights = dict()
    live_colors = dict()
    current_colors = dict()
    # Create a lock for use later
    colorset_lock = Lock()

    def __init__(self):
        if HueLights.logger is None:
            HueLights.logger = logging.getLogger('HueLights')
        HueLights.logger.debug('__init__')

    def setup(self, huelights):
        """ Setup the lights and intialise the colors """
        HueLights.logger.debug('setup: %r', huelights)
        for light, scanval in huelights.items():
            # Only add lights if they have not already been defined
            if HueLights.lights.get(light) is None:
                HueLights.lights[light] = scanval
            if HueLights.live_colors.get(light) is None:
                HueLights.live_colors[light] = (0.0, 0.0, 0.0)

    @property
    def count(self):
        """ Returns the count of lights configured on the system """
        HueLights.logger.debug('Returning %d light', len(HueLights.lights))
        return len(HueLights.lights)

    @property
    def all_lights(self):
        """ Returns a dictionary of the lights scaninfo """
        return HueLights.lights

    @property
    def all_colors(self):
        """ Returns a dictionary of the lights colors """
        return HueLights.live_colors

    def get_light_color(self, name):
        """ Returns the current colour of a light """
        return HueLights.current_colors.get(name)

    def set_light_color(self, name, rgb):
        """ Set a light to a given colour if it exists """
        HueLights.logger.debug('%s : %r', name, rgb)
        if HueLights.live_colors[name]:
            HueLights.live_colors[name] = rgb

    # Locks are used in the set & get of the current colorset to
    # ensure that the server thread is not updating the colorset
    # as the HueUpdate thread is using it to update the lights
    def set_current_colorset(self):
        """ Copy the latest colors ready for an update """
        with HueLights.colorset_lock:
            HueLights.current_colors = copy.deepcopy(HueLights.live_colors)

    def get_current_colorset(self):
        """ Return a copy of the current color set """
        with HueLights.colorset_lock:
            current_colorset = copy.deepcopy(HueLights.current_colors)
        return current_colorset
