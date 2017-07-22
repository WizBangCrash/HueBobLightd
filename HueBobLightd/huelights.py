#!/usr/bin/env python3
"""
HueLight
This module contains a class for managing the lights associated with
the server, taking the updates from the client and ensuring the light's
state is kept up to date.
Also includes a class for updating the lights via requests
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
from threading import Lock
from urllib.request import urlopen, URLError
import requests
from HueBobLightd.colorconvert import Converter, GamutA, GamutB, GamutC


"""
Think about grouping the lights for a client as an autonomous group.
THis would ensure that all lights update when a "sync" command is recieved.
It will also ensure that one light is not updating wth a newer RGB value
than another. Due to a new request coming in while processing the last request.
You could also use grequests to fire off the group of http requests together.
This might ensure that the group all change more in unison.
This may be overkill, but it is worth implemeting and seeing the effects.

NOTE:
Decided against this as it is better to send the latest light value to a
light than to ensure all lights are in sync with "old" values.
"""


class HueLight():
    """
    HueLight class
    Attributes:
        url: url of light (bridge, username portion) NEEDS TO BE in request class
        hue_id: Hue id of light
        name: name of light
        scanarea: (top, bottom, left, right)
        converter: Colour Converter object
        rgb: float tuple(red, green, blue) of new color
        xy_new: int tuple(hue, sat, bri) new color
        xy_previous: int tuple(hue, sat, bri) last color
        in_use: on / off
        lock: lock for accessing rgb member
    """
    logger = None

    #pylint: disable=R0913
    def __init__(self, address, name, hue_id, left, right, top, bottom, brightness, gamut=GamutC):
        if type(self).logger is None:
            type(self).logger = logging.getLogger('HueLight')
        self.lock = Lock()
        self.url = 'http://{}/api/{}'.format(address[0], address[1])
        self.hue_id = hue_id
        self.name = name
        self.brightness = brightness
        self.scanarea = (top, bottom, left, right)
        self.in_use = False
        self.is_on = False
        self.converter = Converter(self._convert_gamut(gamut))
        self.rgb = (0.0, 0.0, 0.0)
        self.xy_new = (0, 0)
        self.xy_previous = (0, 0)
        self.logger.debug('Light: bridge(%r) id(%s) name(%s) created',
                          address[0],
                          self.hue_id,
                          self.name)

    def __repr__(self):
        return '{} {}, {}, ({:d}, {:d}, {:d}, {:d}), {:d}'.format(self.url,
                                                                  self.hue_id,
                                                                  self.name,
                                                                  *self.scanarea,
                                                                  self.brightness)

    @staticmethod
    def _convert_gamut(gamut):
        """ Turn the gamut string into a gamut object """
        # Default is GamutC
        if gamut == 'GamutA':
            result = GamutA
        elif gamut == 'GamutB':
            result = GamutB
        else:
            result = GamutC
        return result

    def _put(self, state, timeout=1):
        """
        Send a PUT request to the specified light
        I use a short timeout on the request because if the bridge is too
        busy to handle it in that time the state would have changed anyway
        """
        result = True
        url = '{}/lights/{}/state'.format(self.url, self.hue_id)
        self.logger.debug('PUT: %s : %r', url, state)
        try:
            resp = requests.put(url=url, json=state, timeout=timeout)
            #pylint: disable=W0613
            if resp.ok:
                self.logger.debug('Response: %s', resp.json())
            else:
                self.logger.debug('Response Error: %s', resp.text)
                result = False
        except requests.exceptions.Timeout:
            self.logger.info('Timeout error for url: %s', url)
            result = False
        except requests.exceptions.ConnectionError:
            self.logger.info('ConnectionError error for url: %s', url)
            result = False

        return result

    def _attributes(self, timeout=1):
        """
        Send a GET Attributes request to the bridge for the specified light
        Return the response as a dcitionary
        """
        self.logger.debug('Get attributes: id(%s), name(%s)',
                          self.name, self.hue_id)
        result = None
        url = '{}/lights/{}'.format(self.url, self.hue_id)
        self.logger.debug('GET: %s', url)
        try:
            resp = requests.get(url=url, timeout=timeout)
            if resp.ok:
                result = resp.json()
                self.logger.debug('Response: %s', result)
            else:
                self.logger.debug('Response Error: %s', resp.text)
        except requests.exceptions.Timeout:
            self.logger.info('Timeout error for url: %s', url)
        except requests.exceptions.ConnectionError:
            self.logger.info('ConnectionError error for url: %s', url)

        return result

    def connect(self):
        """ Attempt to connect to the bridge and return true if successful """
        try:
            urlopen(self.url, timeout=1)
            return True
        except URLError:
            return False

    def validate(self):
        """ Verify with the bridge that this light exists """
        self.in_use = 'state' in self._attributes()
        return self.in_use

    def turn_on(self):
        """ Turn on the light if it is not already on """
        if not self.is_on:
            self.is_on = True
            self.xy_new = self.converter.rgb_to_xy(0.1, 0.1, 0.1)
            state = {
                'on' : True,
                'xy' : [*self.xy_new],
                'bri' : self.brightness
            }
            # Send the update to the light
            self.logger.debug('Turn on light: id(%s), name(%s)',
                            self.hue_id, self.name)
            self._put(state, timeout=1)

    def turn_off(self):
        """ Turn off the light if light is on """
        if self.is_on:
            self.is_on = False
            state = {
                'on' : False,
            }
            # Send the update to the light
            self.logger.debug('Turn off light: id(%s), name(%s)',
                            self.hue_id, self.name)
            self._put(state)

    def set_color(self, red, green, blue):
        """
        Set the light color
            red: float value for red
            green: float value for green
            blue: float value for blue
        We don't do any conversions in this function as it is continually
        called and we don't want to waste time converting the values until
        we actually plan to update the light
        """
        with self.lock:
            self.rgb = (red, green, blue)
        self.logger.debug('Set light(%s) color: %r', self.hue_id, self.rgb)

    def update(self, transition_time=3):
        """
        Send an update to the light if required
        We only send and update if the colour has changed
        We optimise the update to only include the hue commands required i.e.
            if only the hue has changed then we only send a hue command
        We convert the rgb color here as it is done less often than setting
        the color
        """

        # Convert the rbg to hsv
        with self.lock:
            self.xy_new = self.converter.rgb_to_xy(*self.rgb)
        if self.xy_new != self.xy_previous:
            # Colour has changed so build a command to send to the bridge
            self.logger.debug('Light(%s) changed: RGB:%r, XY:%r -> %r',
                              self.hue_id, self.rgb,
                              self.xy_previous, self.xy_new)
            state = {
                'transitiontime' : transition_time
            }
            if self.xy_new != self.xy_previous:
                state['xy'] = [*self.xy_new]

            # Send the update to the light
            # Only update xy_previous if the update request was successful
            if self._put(state):
                self.xy_previous = self.xy_new
        # else:
        #     # Color hasn't changed
        #     self.logger.debug('Light(%s) color has not changed: '
        #                       'RGB:%r, XY:%r == %r',
        #                       self.hue_id,
        #                       self.rgb,
        #                       self.xy_previous, self.xy_new)
