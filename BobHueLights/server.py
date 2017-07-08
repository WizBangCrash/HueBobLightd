#!/usr/bin/env python3
"""
bobhuelightd
This module contains main daemon for the bobhuelightd server
"""

__author__ = "David Dix"
__copyright__ = "Copyright 2017, David Dix"

import logging
import socketserver
from BobHueLights.huelights import HueLights

class BobHueRequestHandler(socketserver.StreamRequestHandler):
    """ My socket request handler """
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('BobHueRequestHandler')
        self.logger.debug('__init__')
        socketserver.StreamRequestHandler.__init__(self, request,
                                                   client_address,
                                                   server)
        self.lights = None
        return

    def setup(self):
        self.logger.debug('setup')
        self.lights = HueLights()
        return socketserver.StreamRequestHandler.setup(self)

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
                self.logger.debug('RX [%s]: %s', self.client_address[0],
                                  request)
                # Process the request
                response = self.process_request(request)

                if response:
                    # Send the response
                    self.logger.debug('TX [%s]: %s', self.client_address[0],
                                      response)
                    self.wfile.write(response.encode())
        except Exception as e:
            self.logger.debug('ER [%s]: %r', self.client_address[0], e)
            raise
        self.logger.debug('DC [%s]: disconnected', self.client_address[0])

    def process_request(self, request):
        """ Process the incoming request """
        response = list()

        # First we check the message format
        message_parts = request.split()
        cmd = message_parts[0]
        if cmd == 'hello':
            """
            This is the connection command.
            Hello command should return 'hello' from the server
            """
            response.append('hello')
        elif cmd == 'ping':
            """
            This command checks if this client is currently using
            any of the lights.
            Return the number of lights in use by this client
            """
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
                response.append('version 5')
            elif subcmd == 'lights':
                """
                Returns the lights declared in server configuration.
                First line is the number of lights, then each line
                corresponds to one light and its scanning parameters.
                """
                response.append('lights {:d}'.format(self.lights.count))
                for name, scaninfo in self.lights.all_lights.items():
                    lightdata = 'light {0} scan {1} {2} {3} {4}'.format(name, *scaninfo)
                    response.append(lightdata)
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
                pass
            if subcmd == 'light': # rbg
                """
                Commands to control what to do with the lights 
                """
                lightcmd = message_parts[2]
                if lightcmd == 'rgb':
                    """
                    Change the color of a light to the given rgb value.
                    Values are floats: R, G, B
                    """
                    pass
                elif lightcmd == 'speed':
                    """
                    Change the transition speed of one light.
                    Value is between 0.0 and 100.0.
                    100 means immediate changes.
                    """
                    pass
                elif lightcmd == 'interpolation':
                    """
                    Enable or disable color interpolation between 2 steps.
                    Value is a boolean ("0"/"1" or "true"/"false")
                    """
                    pass
                elif lightcmd == 'use':
                    """
                    Declare whether a light is used.
                    By default all lights are used.
                    Any color change request for an unused light 
                    will be ignored.
                    """
                    pass
                elif lightcmd == 'singlechange':
                    pass
        elif cmd == 'sync':
            """
            Send synchronised signal to wake the devices and tell
            them request is ready to be read. 
            'allowsync' must be enabled in configuration file.
            Ignored if not allowsync or not synchronized device.
            Should be sent after each bulk set.
            """
            pass

        # Join all the responses into a single string seperated by
        # carriage returs and terminated in a carriage return
        if response:
            return '\n'.join(response) + '\n'
        else:
            return None

    def finish(self):
        self.logger.debug('finish')
        return socketserver.StreamRequestHandler.finish(self)


class BobHueServer(socketserver.TCPServer):
    """ Server listening for LightEffects clients """
    def __init__(self, server_address,
                 handler_class=BobHueRequestHandler,
                ):
        self.logger = logging.getLogger('BobHueServer')
        self.logger.debug('__init__')
        socketserver.TCPServer.__init__(self, server_address,
                                        handler_class)
        return

    def server_activate(self):
        self.logger.debug('server_activate')
        socketserver.TCPServer.server_activate(self)
        return

    def serve_forever(self, poll_interval=0.5):
        self.logger.debug('waiting for request')
        self.logger.info(
            'Handling requests, press <Ctrl-C> to quit'
        )
        socketserver.TCPServer.serve_forever(self, poll_interval)
        return

    def handle_request(self):
        self.logger.debug('handle_request')
        return socketserver.TCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)',
                          request, client_address)
        return socketserver.TCPServer.verify_request(
            self, request, client_address,
        )

    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)',
                          request, client_address)
        return socketserver.TCPServer.process_request(
            self, request, client_address,
        )

    def server_close(self):
        self.logger.debug('server_close')
        return socketserver.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)',
                          request, client_address)
        return socketserver.TCPServer.finish_request(
            self, request, client_address,
        )

    # def close_request(self, request_address):
    #     self.logger.debug('close_request(%s)', request_address)
    #     return socketserver.TCPServer.close_request(
    #         self, request_address,
    #     )

    def shutdown(self):
        self.logger.debug('shutdown()')
        return socketserver.TCPServer.shutdown(self)
