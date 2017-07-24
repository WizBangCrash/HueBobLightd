#!/usr/bin/env python3
"""
LightsUpdater
This module contains a class for sending updates to the lights using the
messages and values recieved from the server
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
from time import time
from threading import Event


class LightsUpdater():
    """
    Class for connecting to the hue bridge and updating the
    configured lights as fast as the bridge will allow
    """
    logger = None

    def __init__(self):
        """
        Initialise the updater thread
        """
        self.exit_event = Event()
        if type(self).logger is None:
            type(self).logger = logging.getLogger('LightsUpdater')
        self.lights = list()
        self.last_synctime = time()
        self.auto_off_delay = 300  # Default to 5 mins

    def add(self, new_light):
        """ Add a light to the list of lights to update """
        # First check that the light does not currently exist in the list
        matches = [
            light for light in self.lights
            if light.name == new_light.name
            and light.hue_id == new_light.hue_id
        ]
        if not matches:
            self.lights.append(new_light)
            self.logger.debug('Added light name(%s), id(%s)',
                              new_light.name, new_light.hue_id)
        else:
            self.logger.debug('Light name(%s), id(%s) already exists',
                              new_light.name, new_light.hue_id)

    def remove(self, light):
        """ Remove the specified light from the list """
        self.logger.debug('Removing light name(%s), id(%s)',
                          light.name, light.hue_id)
        self.lights = [lite for lite in self.lights if lite != light]
        light.turn_off()
        del light

    def update(self):
        """
        Called to request the object to update the lights
        In our implementation we just record the time an update is requested
        as the update_forever method is feeding the bridge as fast as it can
        """
        self.last_synctime = time()
        self.logger.debug('Update request received: %d', self.last_synctime)

    def initialise(self):
        """
        Get the update loop to re-initialise the lights
        """
        self.logger.info('Initialise: Auto Off: %dmins', self.auto_off_delay / 60)
        for light in self.lights:
            if light.validate():
                light.turn_on()
            else:
                self.logger.debug('Light: name(%s), id(%s) does not exist on bridge',
                                  light.name, light.hue_id)

    def shutdown(self):
        """ Turn off the light and disconnect from the bridge """
        self.logger.info('Shutdown called')
        self.exit_event.set()  # Tell the update forever loop to exit
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
            if self.exit_event.wait(timeout=1):
                self.exit_event.clear()
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
        self.logger.info('Update period: %.1fms', update_period * 1000)

        # Main loop for continually updating the lights
        while not self.exit_event.wait(timeout=update_period):
            # Calsulate turn off flag if enabled
            if self.auto_off_delay:
                turn_off = (time() - self.last_synctime) > self.auto_off_delay
            else:
                turn_off = False
            for light in lights_inuse:
                if turn_off:
                    light.turn_off()
                else:
                    light.update()
        self.exit_event.clear()

        self.logger.debug('Exiting update_forever: 2')
