#!/usr/bin/env python3
"""
Configuration File Module
This module contains the functions to read the configuration data
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import os
import collections
import logging
import re
import json
from jsmin import jsmin
import validators

# Globals
BASEDIR = os.path.realpath(os.path.dirname(__file__))


class ConfigParser():
    """
    Class to load a config file and provide ability to
    merge it with others

    See https://stackoverflow.com/questions/25577578/python-access-class-variable-from-instance
    for how to use the class variable 'data'
    """
    logger = None
    data = dict()

    def __init__(self):
        if type(self).logger is None:
            type(self).logger = logging.getLogger('ConfigParser')

    def __remove_trailing_commas(self, json_like):
        """
        Removes trailing commas from *json_like* and returns the result.
        Example::
            >>> remove_trailing_commas('{"foo":"bar","baz":["blah",],}')
            '{"foo":"bar","baz":["blah"]}'
        """
        #pylint: disable=R0201
        trailing_object_commas_re = re.compile(
            r'(,)\s*}(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)')
        trailing_array_commas_re = re.compile(
            r'(,)\s*\](?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)')
        # Fix objects {} first
        objects_fixed = trailing_object_commas_re.sub("}", json_like)
        # Now fix arrays/lists [] and return the result
        return trailing_array_commas_re.sub("]", objects_fixed)

    def _update_config(self, orig, new):
        '''
        Recursive function to handle updating the parameters dictionary
        at all levels
        '''
        #pylint: disable=C0103
        for k, v in new.items():
            if isinstance(v, collections.Mapping):
                r = self._update_config(orig.get(k, {}), v)
                orig[k] = r
            else:
                orig[k] = new[k]
        return orig

    def read_config(self, cfgfile=None):
        '''
        Read in the config file for later reference
        '''
        # Use a default file if none supplied
        # TODO: If a file is provided look for it in CWD and other common places
        if cfgfile is None:
            cfgfile = '{}/bobhuelightd.conf'.format(BASEDIR)
        self.logger.debug('Reading %s', cfgfile)
        if os.path.isfile(cfgfile):
            with open(cfgfile, 'r') as jsonfile:
                config = jsmin(jsonfile.read())
                config = self.__remove_trailing_commas(config)
                type(self).data.update(json.loads(config))
                return True
        else:
            self.logger.error('Failed to load configuration file: %s', cfgfile)
            return False

    def merge_config(self, mergefile):
        '''
        Read in the provided file and merge it with the default config
        Any entries existing in the file will replce those in the
        default connfig
        '''
        self.logger.debug('Merging %s', mergefile)
        if mergefile is None:
            return False
        if not os.path.isfile(mergefile):
            self.logger.error('Merge file does not exist: %s', mergefile)
            return False

        with open(mergefile, 'r') as jsonfile:
            # Read in the file and convert to dictionary
            config = jsmin(jsonfile.read())
            config = self.__remove_trailing_commas(config)
            mergedata = json.loads(config)
            self._update_config(type(self).data, mergedata)
        return True

    def get_parameter(self, param_name, default=None):
        '''
        Return the requested parameter, None if it does not exist,
        or the default if a default is supplied
        '''
        #pylint: disable=R0201
        return self.data.get(param_name, default)


class BobHueConfig(ConfigParser):
    """ Class to manage the configuration file & parameters """

    @property
    def server_port(self):
        """ Return the server port number (default 19333) """
        server = self.data['server']
        port = server.get('port', 19333)
        return port

    @property
    def bridge_address(self):
        """ Return the bridge address """
        # hue_bridge = self.data.get('hueBridge')
        # if hue_bridge:
        #     return self.data.get('address')
        # else:
        #     return None
        return self.data['hueBridge']['address']

    @property
    def username(self):
        """ Return the username """
        # return ConfigParser.data.get('username')
        return self.data['hueBridge']['username']

    def validate(self):
        """ Check the conf file for errors """
        #pylint: disable=R0912
        # Assume all is well
        result = True

        # Check all the mandatory parameters first
        if self.data.get('hueBridge'):
            hue_bridge = self.data['hueBridge']
            if hue_bridge.get('address'):
                address = hue_bridge.get('address')
                if not validators.domain(address) \
                        and not validators.ip_address.ipv4(address):
                    self.logger.error('Incorrect "address" parameter in conf file')
                    result = False
            else:
                self.logger.error('Missing "address" parameter in conf file')
                result = False

            if hue_bridge.get('username'):
                # TODO: validate the Hue username
                pass
            else:
                self.logger.error('Missing "username" parameter in conf file')
                result = False

        if self.data.get('lights'):
            for light in self.data.get('lights'):
                light_id = light.get('id')
                if light_id is None:
                    self.logger.error('Missing "id" parameter in light: %s',
                                      light)
                    result = False
                name = light.get('name')
                if name is None:
                    self.logger.error('Missing "name" parameter in light: %s',
                                      light)
                    result = False
                gamut = light.get('gamut')
                # gamut is optional, so only check if present
                if gamut:
                    if not (gamut == 'GamutA' or gamut == 'GamutB' or gamut == 'GamutC'):
                        self.logger.error('Incorrect "gamut" parameter in light: %s',
                                          light)
                        result = False
                vscan = light.get('vscan')
                if vscan:
                    if vscan.get('top') is None:
                        self.logger.error('Missing "top" parameter in light:'
                                          ' %s', light)
                        result = False
                    if vscan.get('bottom') is None:
                        self.logger.error('Missing "bottom" parameter in light:'
                                          ' %s', light)
                        result = False
                else:
                    self.logger.error('Missing "vscan" parameter in light: %s',
                                      light)
                    result = False
                hscan = light.get('hscan')
                if hscan:
                    if hscan.get('left') is None:
                        self.logger.error('Missing "left" parameter in light:'
                                          ' %s', light)
                        result = False
                    if hscan.get('right') is None:
                        self.logger.error('Missing "right" parameter in light:'
                                          ' %s', light)
                        result = False
                else:
                    self.logger.error('Missing "hscan" parameter in light: %s',
                                      light)
                    result = False
        else:
            self.logger.error('Missing "lights" parameter in conf file')
            result = False

        # Now check all the optional parameters
        if self.data.get('server'):
            server = ConfigParser.data['server']
            if not server.get('port'):
                self.logger.error('Missing "port" parameter in "server"')
                result = False
            elif not isinstance(server.get('port'), int):
                self.logger.error('"port" parameter not integer in "server"')
                result = False

        return result
