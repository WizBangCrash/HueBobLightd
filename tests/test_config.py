#!/usr/bin/env python3
"""
Test HueConfig class
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import os
import pytest
import mock
from BobHueLights.config import BobHueConfig

# Globals
BASEDIR = os.path.realpath(os.path.dirname(__file__))


class TestHueConfig():
    """ Test the HueConfig class """
    #pylint: disable=W0212,W0201
    def setup(self):
        """ Create a ClientAPI object """
        self.config = BobHueConfig()

    def test_read_good_file(self):
        """ Read in a good config file and check all the values """
        assert self.config.read_config('{}/data/bobhuelightd-good.conf'
                                       .format(BASEDIR))

        assert self.config.bridge_address == '192.168.1.1'
        assert self.config.username == '<hue api user name>'

        lights = self.config.lights
        assert 'strip' in lights.keys()
        assert lights['right'] == (50, 100, 70, 100)
        assert lights['left'] == (50, 100, 0, 30)

    def test_read_file_extra_commas(self):
        """ REad a conf file with trailing commas """
        assert self.config.read_config('{}/data/bobhuelightd-commas.conf'
                                       .format(BASEDIR))

    def test_read_bad_file(self):
        """ Read a bad config file and check it gives correct errors """
        assert not self.config.read_config('{}/data/bad.conf'.format(BASEDIR))

        assert self.config.read_config('{}/data/bobhuelightd-bad.conf'
                                       .format(BASEDIR))
        assert not self.config.validate()
