#!/usr/bin/env python3
"""
HueUpdate
This module contains a class for updating the lights associated with
the server.
The intention is to feed the updates as fast as possible to the Hue Bridge.
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
import copy
import time
from colorsys import rgb_to_hsv
import requests
from BobHueLights.huelights import HueLights


class HueUpdate():
    """
    Class for connecting to the Hue bridge and updating the
    configured lights as fast as the bridge will allow
    """
    logger = None

    def __init__(self, bridge, username):
        """
        Initialise the updater thread:
            bridge: FQDN or IP address of Hue bridge
            username: Authorised user of the Hue bridge
            lights: List of Hue bridge light id's to update
        """
        if HueUpdate.logger is None:
            HueUpdate.logger = logging.getLogger('HueUpdate')
        self.url = 'http://{}/api/{}'.format(bridge, username)
        self.lights = HueLights()
        HueUpdate.logger.debug('Initialised with %d lights', self.lights.count)
    
    def connect(self):
        """ Connect to the Hue bridge """
        # TODO: Validate the bridge address
        # TODO: Move the request calls into own class
        response = requests.get(url='{}/config'.format(self.url))
        state = {
            'on' : True,
            'xy' : [0.4, 0.4],
            'bri' : 50,
            'alert' : 'select'
        }
        for light in self.lights.all_lights:
            url = '{}/lights/{}/state'.format(self.url, light)
            try:
                response = requests.put(url=url, json=state)
                HueUpdate.logger.debug('Change:\n%s', response.json())
            except requests.exceptions.Timeout:
                HueUpdate.logger.exception('Timeout error for url: %s', self.url)

        # TODO: Do some checking in this function and return false if failures
        return True

    def shutdown(self):
        """ Turn off the light and disconnect from the bridge """
        for light in self.lights.all_lights.keys():
            state = {
                'on' : False,
            }
            url = '{}/lights/{}/state'.format(self.url, light)
            try:
                response = requests.put(url=url, json=state)
                if response.ok:
                    HueUpdate.logger.debug('Change:\n%s', response.json())
                else:
                    HueUpdate.logger.debug('Change Error:\n%s', response.text)
            except requests.exceptions.Timeout:
                HueUpdate.logger.exception('Timeout error for url: %s', self.url)

    def update(self):
        """
        Take a snapshot of the current light colours and send
        an update to the Hue Bridge if any have changed
        """
        last_colors = dict()
        changed = dict()
        while True:
            time.sleep(0.3)
            changed.clear()
            current_colors = self.lights.get_current_colorset()
            HueUpdate.logger.debug('Current: %r', current_colors)
            HueUpdate.logger.debug('Last: %r', last_colors)
            for light, color in current_colors.items():
                if last_colors.get(light) != color:
                    # Convert to HSV for Hue Bridge
                    # Hue, Saturation, Brightness
                    # Hue : 0 to 65535
                    # Saturation: 254 to 0
                    # Brightness: 1 to 254
                    hue, sat, bri = rgb_to_hsv(*color)
                    changed[light] = (hue * 65535, sat * 254, bri * 254)
            if current_colors != last_colors:
                last_colors = copy.deepcopy(current_colors)
            if changed:
                HueUpdate.logger.debug('Changed lights: %r', changed)

            # Update the bridge
            for light, values in changed.items():
                state = {
                    'on' : True,
                    'hue' : int(values[0]),
                    'sat' : int(values[1]),
                    'bri' : int(values[2]),
                    'transitiontime' : 3
                }
                url = '{}/lights/{}/state'.format(self.url, light)
                try:
                    response = requests.put(url=url, json=state)
                    if response.ok:
                        HueUpdate.logger.debug('Change:\n%s', response.json())
                    else:
                        HueUpdate.logger.debug('Change Error:\n%s', response.text)
                except requests.exceptions.Timeout:
                    HueUpdate.logger.exception('Timeout error for url: %s', self.url)
