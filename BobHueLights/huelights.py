#!/usr/bin/env python3
"""
cls
This module contains a class for managing the lights associated with
the server, taking the updates from the client and ensuring the light's
state is kept up to date.
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
from time import sleep
from threading import Lock
from urllib.request import urlopen, URLError
import requests
from BobHueLights.colorconvert import Converter, GamutA, GamutB, GamutC


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


class HueRequest():
    """ Class to send http requests to the hue bridge """
    #pylint: disable=R0903
    logger = None
    url = None

    @classmethod
    def __init__(cls, bridge, username):
        if cls.logger is None:
            cls.logger = logging.getLogger('HueLight')
        cls.url = 'http://{}/api/{}'.format(bridge, username)

    @classmethod
    def connect(cls):
        """ Attempt to connect to the bridge and return true if successful """
        try:
            urlopen(cls.url, timeout=1)
            return True
        except URLError:
            return False

    @classmethod
    def put_response(cls, resp, *args, **kwargs):
        """ Asynchronous response to the put requests """
        #pylint: disable=W0613
        if resp.ok:
            cls.logger.debug('Change: %s', resp.json())
        else:
            cls.logger.debug('Change Error: %s', resp.text)

    @classmethod
    def put(cls, name, state, timeout=1):
        """
        Send a PUT request to the specified light
        I use a short timeout on the request because if the bridge is too
        busy to handle it in that time the state would have changed anyway
        I send the request asynchronously i.e. not waiting for the response,
        as I do not want to hold up the other lights requests.
        """
        url = '{}/lights/{}/state'.format(cls.url, name)
        cls.logger.debug('PUT: %s : %r', url, state)
        try:
            requests.put(url=url, json=state,
                         hooks={'response' : cls.put_response},
                         timeout=timeout)
        except requests.exceptions.Timeout:
            cls.logger.info('Timeout error for url: %s', url)
        except requests.exceptions.ConnectionError:
            cls.logger.info('ConnectionError error for url: %s', url)

class HueLight():
    """
    cls class
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
    Methods:
        on: Turn on light
        off: turn off light
        set_color: new rgb values
        update: send request to bridge
            transistion_time = 3,
            alert = None
            effect = None
    """
    logger = None

    #pylint: disable=R0913
    def __init__(self, name, hue_id, left, right, top, bottom, gamut=GamutC):
        if type(self).logger is None:
            type(self).logger = logging.getLogger('HueLight')
        self.lock = Lock()
        self.hue_id = hue_id
        self.name = name
        self.scanarea = (top, bottom, left, right)
        self.in_use = False
        self.converter = Converter(self.convert_gamut(gamut))
        self.rgb = (0.0, 0.0, 0.0)
        self.xy_new = (0, 0)
        self.xy_previous = (0, 0)
        self.logger.info('Created light: %s(%d, %d, %d, %d)',
                         hue_id, left, right, top, bottom)

    @staticmethod
    def convert_gamut(gamut):
        """ Turn the gamut string into a gamut object """
        # Default is GamutC
        if gamut == 'GamutA':
            result = GamutA
        elif gamut == 'GamutB':
            result = GamutB
        else:
            result = GamutC
        return result

    def turn_on(self):
        """ Turn on the light """
        self.in_use = True
        self.xy_new = self.converter.rgb_to_xy(0.1, 0.1, 0.1)
        state = {
            'on' : True,
            'xy' : [*self.xy_new],
            'alert' : 'select'
        }
        # Send the update to the light
        HueLight.logger.debug('Turn on light: "%s"', self.hue_id)
        HueRequest.put(self.hue_id, state, timeout=1)

    def turn_off(self):
        """ Turn off the light """
        self.in_use = False
        state = {
            'on' : False,
        }
        # Send the update to the light
        HueLight.logger.debug('Turn off light: "%s"', self.hue_id)
        HueRequest.put(self.hue_id, state)

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
        HueLight.logger.debug('Set light(%s) color: %r', self.hue_id, self.rgb)

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
        if self.xy_new == self.xy_previous:
            # Color hasn't changed. Nothing to do, so return
            HueLight.logger.debug('Light(%s) color has not changed: '
                                  'RGB:%r, XY:%r == %r',
                                  self.hue_id,
                                  self.rgb,
                                  self.xy_previous, self.xy_new)
            return

        # Colour has changed so build a command to send to the bridge
        HueLight.logger.debug('Light(%s) changed: RGB:%r, XY:%r -> %r',
                              self.hue_id, self.rgb,
                              self.xy_previous, self.xy_new)
        state = {
            'transitiontime' : transition_time
        }
        if self.xy_new != self.xy_previous:
            state['xy'] = [*self.xy_new]

        # Send the update to the light
        HueRequest.put(self.hue_id, state)
        # TODO: only update xy_previous if the request was successful
        self.xy_previous = self.xy_new


class HueUpdate():
    """
    Class for connecting to the Hue bridge and updating the
    configured lights as fast as the bridge will allow
    """
    logger = None

    def __init__(self, lights):
        """
        Initialise the updater thread:
            lights: List of HueLight objects
        """
        if type(self).logger is None:
            type(self).logger = logging.getLogger('HueUpdate')
        self.lights = lights
        HueUpdate.logger.debug('Initialised with %d lights', len(lights))

    def connect(self):
        """ Connect to the Hue bridge """
        # TODO: Look at how we add a connection timeout to the PUT and handle it
        for light in self.lights:
            light.turn_on()
        return True

    def shutdown(self):
        """ Turn off the light and disconnect from the bridge """
        for light in self.lights:
            light.turn_off()

    def update_forever(self):
        """
        Take a snapshot of the current light colours and send
        an update to the Hue Bridge if any have changed
        """
        while True:
            sleep(0.3)
            for light in self.lights:
                light.update()
