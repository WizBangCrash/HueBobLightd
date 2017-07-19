#!/usr/bin/env python3
"""
LightsUpdater
This module contains a class for sending updates to the lights using the
messages and values recieved from the server
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
from threading import Event
from HueBobLightd.huelights import HueLight


class LightsUpdater():
    """
    Class for connecting to the Hue bridge and updating the
    configured lights as fast as the bridge will allow
    """
    logger = None

    def __init__(self, transition=3):
        """
        Initialise the updater thread
            transition: x * 100ms tranition between updates
        """
        self.event = Event()
        if type(self).logger is None:
            type(self).logger = logging.getLogger('LightsUpdater')
        self.lights = list()
        self.transition = transition
        self.logger.info('Intialised with transition time of %dms',
                         self.transition * 100)

    # def connect(self):
    #     """ Connect to the Hue bridge """
    #     self.logger.debug('Connect called')
    #     return HueRequest.connect()

    #pylint: disable=R0913
    def add(self, address, light_name, light_id, light_scan, light_bri, light_gamut):
        """ Add a light to the list of lights to update """
        self.logger.debug('Adding light bridge(%s) id(%s), name(%s)',
                          address[0], light_id, light_name)
        light = HueLight(address, light_name, light_id, *light_scan, light_bri, light_gamut)
        self.lights.append(light)

    def remove(self, light):
        """ Remove the specified light from the list """
        self.logger.debug('Removing light id(%s), name(%s)',
                          light.hue_id, light.name)
        self.lights = [lite for lite in self.lights if lite != light]
        light.turn_off()
        del light

    def initialise(self):
        """ Get the update loop to re-initialise the lights """
        self.logger.debug('Initialise called')
        for light in self.lights:
            if light.validate():
                light.turn_on()
            else:
                self.logger.debug('Light: id(%s) name(%s) does not exist on bridge',
                                  light.hue_id, light.name)

    def shutdown(self):
        """ Turn off the light and disconnect from the bridge """
        self.logger.info('Shutdown called')
        self.event.set()  # Tell the update forever loop to exit
        for light in self.lights:
            self.remove(light)

    def update_forever(self):
        """
        Main loop for updating the lights
        Handles connecting to the bridge, turning on the lights and
        sending the colour updates
        """
        # TODO: We need to check all available bridges
        while not self.lights[0].connect():
            self.logger.error('Failed to connect to hue bridge. Retrying...')
            if self.event.wait(timeout=1):
                self.event.clear()
                self.logger.debug('Exiting update_forever: 1')
                return
        self.logger.info('Connection established to hue bridge')

        self.initialise()
        self.logger.info('Lights have been turned on')

        """
        The update loop timeout is governed by the number of lights we need
        to update.
        Philips recommend no more than 10 requests per second, so we
        multiply 0.1s by the number of lights we have
        We also adjust the transistion time to ensure a light has
        completed its update before the next update arrives
        """
        lights_inuse = [light for light in self.lights if light.in_use]
        # self.logger.info('Lights in_use = %d', len(lights_inuse))
        update_period = 0.1 * len(lights_inuse)
        transition_time = self.transition if self.transition < 4 else 3
        self.logger.info('Update period: %.1fms, transition time %dms',
                         update_period * 1000, transition_time * 100)

        # Only update if light is in use
        # Main loop for continually updaing the lights
        while not self.event.wait(timeout=update_period):
            for light in lights_inuse:
                light.update(transition_time=transition_time)
        self.event.clear()

        self.logger.debug('Exiting update_forever: 2')
