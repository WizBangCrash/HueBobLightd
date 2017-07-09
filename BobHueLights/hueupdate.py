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
from colorsys import rgb_to_hls
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
        if self.logger is None:
            self.logger = logging.getLogger('HueUpdate')
        self.url = 'http://{}/api/{}'.format(bridge, username)
        self.lights = HueLights()
        self.logger.debug('Initialised with %d lights', self.lights.count)
    
    def connect(self):
        """ Connect to the Hue bridge """
        # TODO: Validate the bridge address
        url = '{}/config'.format(self.url)
        response = requests.get(url=url)
        if response.ok:
            self.logger.debug('Bridge Config:\n%s', response.json())
            result = True
        else:
            self.logger.debug('Bridge Error:\n%s', response.text)
            result = False
        return result

    def shutdown(self):
        """ Turn off the light and disconnect from the bridge """
        pass

    def update(self):
        """
        Take a snapshot of the current light colours and send
        an update to the Hue Bridge
        """
        last_colors = dict()
        changed = dict()
        while True:
            time.sleep(0.5)
            changed.clear()
            current_colors = self.lights.all_colors
            for light, color in current_colors.items():
                if last_colors.get(light) != color:
                    # Convert to HSV for Hue Bridge
                    # Hue, Saturation, Brightness
                    # Hue : 0 to 65535
                    # Saturation: 254 to 0
                    # Brightness: 1 to 254
                    hue, sat, bri = rgb_to_hsv(*color)
                    # hue, bri, sat = rgb_to_hls(*color)
                    changed[light] = (hue * 65535, sat * 254, bri * 254)
            if current_colors != last_colors:
                self.logger.info('Current light values:\n%r', current_colors)
                last_colors = copy.deepcopy(current_colors)
            if changed:
                self.logger.info('Changed lights: %r', changed)

            # Update the bridge
            for light, values in changed.items():
                state = {
                    'on' : True,
                    'hue' : int(values[0]),
                    'sat' : int(values[1]),
                    'bri' : int(values[2]),
                    'transitiontime' : 4
                }
                url = '{}/lights/{}/state'.format(self.url, light)
                response = requests.put(url=url, json=state)
                if response.ok:
                    self.logger.debug('Change:\n%s', response.json())
                else:
                    self.logger.debug('Change Error:\n%s', response.text)


# try:
#     result = requests.post(url=url,
#                             auth=HTTPBasicAuth(self.sak, None),
#                             json=data)
#     break
# except requests.exceptions.Timeout:
#     logging.exception('Timeout error for url: %s', url)
#     retry_count = retry_count - 1
# except requests.exceptions.RequestException as excp:
#     logging.exception('Request error for url: %s', url)
#     raise

# try:
#     logging.debug('url=%s, hook=%r', url, hook)
#     response = requests.get(url=url,
#                             auth=HTTPBasicAuth(self.sak, None),
#                             hooks={'response' : hook})
#     if response.ok:
#         if 'version' in url:
#             # Special case as the result in the response.text
#             result = response.text.strip('"')
#         else:
#             # Return the list of networks as a JSON object
#             result = response.json()
#     break
# except ValueError:
#     # JSON decode error
#     logging.debug('JSON decode error for url: %s, resp.text: %r',
#                     url, response.text)
#     break
# except requests.exceptions.Timeout:
#     logging.exception('Timeout error for url: %s', url)
#     retry_count = retry_count - 1
# except requests.exceptions.RequestException as excp:
#     logging.exception('Request error for url: %s', url)
#     raise
