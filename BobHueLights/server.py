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
            while True:
                request = self.rfile.readline()
                if not request:
                    break
                request = request.strip()
                self.logger.debug('RX [%s]: %s', self.client_address[0], request)

                response = self.process_request(request.decode()).encode()

                self.logger.debug('TX [%s]: %s', self.client_address[0], response)
                self.wfile.write(response)
        except Exception as e:
            self.logger.debug('ER [%s]: %r', self.client_address[0], e)
            raise
        self.logger.debug('DC [%s]: disconnected', self.client_address[0])

    def process_request(self, request):
        """ Process the incoming request """
        response = list()
        data = request

        # First we check the message format
        message_parts = data.split()
        if message_parts is None:
            self.logger.debug('Null message recieved')
            return None

        cmd = message_parts[0]
        if cmd == 'hello':
            self.logger.debug('Got: hello')
            response.append('hello\n')
        elif cmd == 'ping':
            self.logger.debug('Got: ping')
            response.append('ping 1\n')
        elif cmd == 'get':
            subcmd = message_parts[1]
            self.logger.debug('Got: %s:%s', cmd, subcmd)
            if subcmd == 'version':
                response.append('version 5\n')
            elif subcmd == 'lights':
                self.logger.debug('Sending: lights 1')
                response.append('lights {}\n'.format(self.lights.count))
                self.logger.debug('Sending: light 001 scan 0.0, 100.0, 0.0, 100.0')
                response.append('light 001 scan {}\n'.format(self.lights.scanarea(1)))

        return ''.join(response)
        # TODO: use this statement to put in the '\n'

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
