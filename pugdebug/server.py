# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import socket

class PugdebugServer():

    sock = None
    address = None

    is_connected = False

    def connect(self):
        self.is_connected = True

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(None)

        try:
            server.bind(('', 9000))
            self.init_connection(server)
        except OSError:
            self.is_connected = False
            print("Socket bind failed")
        finally:
            server.close()

    def init_connection(self, server):
        server.listen(5)

        print('Waiting for connection ...')

        self.sock, self.address = server.accept()
        self.sock.settimeout(None)
        self.read_init_message()

    def read_init_message(self):
        message = self.receive_message()
        print(message)

    def receive_message(self):
        length = self.get_message_length()
        body = self.get_message_body(length)

        return body

    def get_message_length(self):
        length = ''

        while True:
            character = self.sock.recv(1)

            if character.isdigit():
                length = length + character.decode('utf-8')

            if character.decode('utf-8') == '\0':
                return int(length)

    def get_message_body(self, length):
        body = ''

        while length > 0:
            data = self.sock.recv(length)

            body = body + data.decode('utf-8')

            length = length - len(data)

        return body
