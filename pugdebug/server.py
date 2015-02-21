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
    init_message = ''
    last_message = ''

    xdebug_encoding = 'iso-8859-1'

    def connect(self):
        self.is_connected = True

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(None)

        try:
            server.bind(('', 9000))
            self.init_connection(server)
        except OSError:
            self.is_connected = False
            print(OSError.strerror())
            print("Socket bind failed")
        finally:
            server.close()

    def close(self):
        if self.sock is not None:
            self.is_connected = False
            self.sock.close()
            self.sock = None

    def command(self, command):
        self.sock.send(bytes(command + '\0', 'utf-8'))
        self.read_last_message()

    def init_connection(self, server):
        server.listen(5)

        print('Waiting for connection ...')

        self.sock, self.address = server.accept()
        self.sock.settimeout(None)
        self.read_init_message()

    def read_init_message(self):
        self.init_message = self.receive_message()

    def get_init_message(self):
        return self.init_message

    def read_last_message(self):
        self.last_message = self.receive_message()

    def get_last_message(self):
        return self.last_message

    def receive_message(self):
        length = self.get_message_length()
        body = self.get_message_body(length)

        return body

    def get_message_length(self):
        length = ''

        while True:
            character = self.sock.recv(1)

            if self.is_eof(character):
                self.close()

            if character.isdigit():
                length = length + character.decode(self.xdebug_encoding)

            if character.decode(self.xdebug_encoding) == '\0':
                if length == '':
                    return 0
                return int(length)

    def get_message_body(self, length):
        body = ''

        while length > 0:
            data = self.sock.recv(length)

            if self.is_eof(data):
                self.close()

            body = body + data.decode(self.xdebug_encoding)

            length = length - len(data)

        self.get_null()

        return body

    def get_null(self):
        while True:
            character = self.sock.recv(1)

            if self.is_eof(character):
                self.close()

            if character.decode(self.xdebug_encoding) == '\0':
                return

    def is_eof(self, data):
        return data.decode(self.xdebug_encoding) == ''
