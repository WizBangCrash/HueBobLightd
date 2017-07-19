#!/usr/bin/env python3
"""
Socket Server
This module contains main daemon for the bobhuelightd server
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
import socketserver
from HueBobLightd.huelights import HueLight

class BobHueRequestHandler(socketserver.StreamRequestHandler):
    """ My socket request handler """
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('BobHueRequestHandler')
        # self.logger.debug('__init__')
        super().__init__(request, client_address, server)
        return

    # def setup(self):
    #     self.logger.debug('setup')
    #     return super()

    def handle(self):
        self.logger.debug('handle')
        try:
            # Keep reading requests until the client closes the socket
            while True:
                request = self.rfile.readline()
                if not request:
                    break
                # Decode the request into a string and strip unwanted whitespace
                request = request.decode().strip()
                self.logger.debug('RX [%s]: %s', self.client_address[0], request)
                # Process the request
                response = self.process_request(request)

                if response:
                    # Send the response
                    self.logger.debug('TX [%s]: %s', self.client_address[0], response)
                    self.wfile.write(response.encode())
        except Exception as exc:
            self.logger.error('ER [%s]: %r', self.client_address[0], exc)
            raise
        self.logger.debug('DC [%s]: disconnected', self.client_address[0])

    def process_request(self, request):
        """ Process the incoming request """
        #pylint: disable=R0912
        response = list()
        lights = self.server.data

        # First we check the message format
        message_parts = request.split()
        cmd = message_parts[0]
        if cmd == 'hello':
            """
            This is the connection command.
            Hello command should return 'hello' from the server
            """
            self.logger.info('hello')
            response.append('hello')
        elif cmd == 'ping':
            """
            This command checks if this client is currently using
            any of the lights.
            Return the number of lights in use by this client
            """
            self.logger.info('ping')
            response.append('ping 1')
        elif cmd == 'get':
            """
            This command is used to get information about the server protocol
            and it's configured lights
            """
            subcmd = message_parts[1]
            if subcmd == 'version':
                """
                Returns the protocol version used by the server,
                current version is 5.
                """
                self.logger.info('version')
                response.append('version 5')
            elif subcmd == 'lights':
                """
                Returns the lights declared in server configuration.
                First line is the number of lights, then each line
                corresponds to one light and its scanning parameters e.g.

                lights 1
                light 1 scan top, bottom, left, right
                """
                self.logger.info('lights')
                response.append('lights {:d}'.format(len(lights)))
                for light in lights:
                    lightdata = \
                        'light {0} scan {1} {2} {3} {4}'.format(light.hue_id,
                                                                *light.scanarea)
                    response.append(lightdata)
                    self.logger.debug('Response: %s', lightdata)
        elif cmd == 'set':
            """
            This command is used to change lights and client parameters.
            None of them return any information
            """
            subcmd = message_parts[1]
            if subcmd == 'priority':
                """
                Change the client priority, from 0 to 255, default is 128.
                The highest priority is the lowest number
                """
                self.logger.info('priority: %d', int(message_parts[2]))
            if subcmd == 'light':
                """
                Commands to control what to do with the lights
                """
                lightid = message_parts[2]
                lightcmd = message_parts[3]
                if lightcmd == 'rgb':
                    """
                    Change the color of a light to the given rgb value.
                    Values are floats: R, G, B  e.g.
                    set light right rgb 0.000000 0.000000 0.000000
                    """
                    self.logger.debug('light %s rgb: %f, %f, %f', lightid,
                                      float(message_parts[4]),
                                      float(message_parts[5]),
                                      float(message_parts[6]))
                    if len(message_parts) == 7:
                        light = next((x for x in lights if x.hue_id == lightid), None)
                        if light:
                            light.set_color(float(message_parts[4]),  # red
                                            float(message_parts[5]),  # green
                                            float(message_parts[6]))  # blue
                elif lightcmd == 'speed':
                    """
                    Change the transition speed of one light.
                    Value is between 0.0 and 100.0.
                    100 means immediate changes.
                    NOTE: Hue lights are not fast, so no point in processing
                          this command
                    """
                    self.logger.info('light %s speed: %f', lightid,
                                     float(message_parts[4]))
                elif lightcmd == 'interpolation':
                    """
                    Enable or disable color interpolation between 2 steps.
                    Value is a boolean ("0"/"1" or "true"/"false")

                    NOTE: I ignore this command as Hue lights will always
                          interpolate
                    """
                    self.logger.info('light %s interpolation: %d', lightid,
                                     int(message_parts[4]))
                elif lightcmd == 'use':
                    """
                    Declare whether a light is used.
                    By default all lights are used.
                    Any color change request for an unused light
                    will be ignored.
                    """
                    self.logger.info('light %s use: %d', lightid,
                                     int(message_parts[4]))
                    # TODO: Turn on the light if I'm told to use it
                elif lightcmd == 'singlechange':
                    """
                    NOTE: I ignore this command as Hue lights will always
                          transition over time
                    """
                    self.logger.info('light %s singlechange', lightid)
        elif cmd == 'sync':
            """
            Send synchronised signal to HueLights to tell
            it a request is ready to be read.
            'allowsync' should be enabled in configuration file.
            NOTE: In my version I ignore the setting of this option
                  as I know MrMC always sends a sync.
            Should be sent after each bulk set.
            """
            self.logger.debug('sync')
        else:
            # If we get here then we do not recognise the command
            self.logger.info('Unrecognised command: %r', message_parts)

        # Join all the responses into a single string seperated by
        # carriage returs and terminated in a carriage return
        return '\n'.join(response) + '\n' if response else None

    # def finish(self):
    #     self.logger.debug('finish')
    #     return super()


class BobHueServer(socketserver.TCPServer):
    """ Server listening for LightEffects clients """
    pass
    # def __init__(self, server_address, handler_class):
    #     self.logger = logging.getLogger('BobHueServer')
    #     self.logger.debug('__init__')
    #     socketserver.TCPServer.__init__(self, server_address, handler_class)

    # def server_activate(self):
    #     self.logger.debug('server_activate')
    #     socketserver.TCPServer.server_activate(self)
    #     return

    # def serve_forever(self, poll_interval=0.5):
    #     self.logger.debug('waiting for request')
    #     self.logger.info(
    #         'Handling requests, press <Ctrl-C> to quit'
    #     )
    #     socketserver.TCPServer.serve_forever(self, poll_interval)
    #     return

    # def handle_request(self):
    #     self.logger.debug('handle_request')
    #     return socketserver.TCPServer.handle_request(self)

    # def verify_request(self, request, client_address):
    #     self.logger.debug('verify_request(%s, %s)',
    #                       request, client_address)
    #     return socketserver.TCPServer.verify_request(
    #         self, request, client_address,
    #     )

    # def process_request(self, request, client_address):
    #     self.logger.debug('process_request(%s, %s)',
    #                       request, client_address)
    #     return socketserver.TCPServer.process_request(
    #         self, request, client_address,
    #     )

    # def server_close(self):
    #     self.logger.debug('server_close')
    #     return socketserver.TCPServer.server_close(self)

    # def finish_request(self, request, client_address):
    #     self.logger.debug('finish_request(%s, %s)',
    #                       request, client_address)
    #     return socketserver.TCPServer.finish_request(
    #         self, request, client_address,
    #     )

    # # def close_request(self, request_address):
    # #     self.logger.debug('close_request(%s)', request_address)
    # #     return socketserver.TCPServer.close_request(
    # #         self, request_address,
    # #     )

    # def shutdown(self):
    #     self.logger.debug('shutdown()')
    #     return socketserver.TCPServer.shutdown(self)
