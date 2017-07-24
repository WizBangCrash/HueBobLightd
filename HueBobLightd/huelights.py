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
This would ensure that all lights update when a "sync" command is recieved.
It will also ensure that one light is not updating wth a newer RGB value
than another. Due to a new request coming in while processing the last request.
You could also use grequests to fire off the group of http requests together.
This might ensure that the group all change more in unison.
This may be overkill, but it is worth implemeting and seeing the effects.

NOTE:
Decided against this as it is better to send the latest light value to a
light than to ensure all lights are in sync with "old" values.
"""


#pylint: disable=R0902
class HueLight():
    """
    HueLight class
    Attributes:
        lock: lock for accessing rgb member
        url: url of light (bridge, username portion) NEEDS TO BE in request class
        hue_id: Hue id of light
        name: name of light
        brightness: Initial brightness of light
        scanarea: (top, bottom, left, right)
        converter: Colour Converter object
        rgb: float tuple(red, green, blue) of new color
        xy_new: int tuple(hue, sat, bri) new color
        xy_previous: int tuple(hue, sat, bri) last color
        in_use: on / off
    """
    logger = None

    def __init__(self, **kwargs):
        if type(self).logger is None:
            type(self).logger = logging.getLogger('HueLight')
        self.lock = Lock()
        self.in_use = False
        self.is_on = False
        self.rgb = (0.0, 0.0, 0.0)
        self.xy_new = (0, 0)
        self.xy_previous = (0, 0)
        self.name = kwargs.get('name')
        if self.name is None:
            raise ValueError('Light name has no value')
        address = kwargs.get('address')
        if address is None:
            raise ValueError('Light address has no value')
        self.url = 'http://{}/api/{}'.format(address[0], address[1])
        self.hue_id = kwargs.get('hue_id')
        if self.hue_id is None:
            raise ValueError('Light id has no value')
        self.brightness = kwargs.get('brightness', 150)
        self.converter = Converter(self._get_gamut(kwargs.get('gamut', 'GamutC')))
        self.scanarea = kwargs.get('scanarea', (0, 100, 0, 100))
        self.transition = kwargs.get('transition', 3)
        self.logger.debug('Light: %r', self)
        # self.logger.debug('Light: name(%s) initialised: bridge(%r) id(%s) area%r, gamut(%s)',
        #                   self.name, address[0], self.hue_id,
        #                   self.scanarea, kwargs.get('gamut'))

    def __repr__(self):
        # TODO: Figure out how to just return the ip address
        # TODO: figure out how to show the gamut
        return (
            'HueLight: address({}), name({}), id({}), '
            'brightness({:d}), transition({:d}), scanarea{!r}, '
            'gamut({!r})'
        ).format(self.url, self.name, self.hue_id,
                 self.brightness, self.transition, self.scanarea,
                 self.converter)

    @staticmethod
    def _get_gamut(gamut):
        """ Turn the gamut string into a gamut object """
        gamuts = {
            'gamuta' : GamutA,
            'gamutb' : GamutB,
            'gamutc' : GamutC  # Default
        }
        return gamuts.get(gamut.lower(), GamutC)

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
        self.logger.debug('Get attributes: name(%s), id(%s)',
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
        self.logger.info('Connect: %s', self.url)
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
            self.logger.debug('Turn on light: name(%s), id(%s)',
                              self.name, self.hue_id)
            self._put(state, timeout=1)

    def turn_off(self):
        """ Turn off the light if light is on """
        if self.is_on:
            self.is_on = False
            state = {
                'on' : False,
            }
            # Send the update to the light
            self.logger.debug('Turn off light: name(%s), id(%s)',
                              self.name, self.hue_id)
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
        self.logger.debug('Set light(%s) color: %r', self.name, self.rgb)

    def update(self):
        """
        Send an update to the light if required
        We only send and update if the colour has changed
        We convert the rgb color here as it is done less often than setting
        the color
        """

        # Convert the rbg to hsv
        with self.lock:
            self.xy_new = self.converter.rgb_to_xy(*self.rgb)

        if self.xy_new != self.xy_previous:
            # Colour has changed so build a command to send to the bridge
            self.logger.debug('Light(%s:%s) changed: RGB:%r, XY:%r -> %r',
                              self.name, self.hue_id, self.rgb,
                              self.xy_previous, self.xy_new)
            state = {
                'transitiontime' : self.transition,
                'xy' : [*self.xy_new]
            }
            # If the light has been turned off due to autoOff then turn it on
            if not self.is_on:
                state['on'] = True
                state['bri'] = self.brightness

            # Send the update to the light
            # Only update xy_previous if the update request was successful
            if self._put(state):
                self.xy_previous = self.xy_new
        # else:
        #     # Color hasn't changed
        #     self.logger.debug('Light(%s:%s) color has not changed: '
        #                       'RGB:%r, XY:%r == %r',
        #                       self.name, self.hue_id,
        #                       self.rgb,
        #                       self.xy_previous, self.xy_new)
