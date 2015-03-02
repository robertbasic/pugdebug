# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import socket

from PyQt5.QtCore import QByteArray, pyqtSignal
from PyQt5.QtNetwork import QTcpServer, QHostAddress

class PugdebugServer(QTcpServer):

    sock = None

    last_message = ''

    xdebug_encoding = 'iso-8859-1'

    last_message_read_signal = pyqtSignal()

    def __init__(self):
        super(PugdebugServer, self).__init__()

        self.newConnection.connect(self.handle_new_connection)

    def connect(self):
        if self.isListening():
            return True

        self.listen(QHostAddress.Any, 9000)

    def disconnect(self):
        self.sock = None
        self.last_message = ''

        self.close()

    def handle_new_connection(self):
        if self.hasPendingConnections():
            self.sock = self.nextPendingConnection()
            self.sock.readyRead.connect(self.handle_ready_read)

    def command(self, command):
        if not self.sock is None:
            self.sock.write(bytes(command + '\0', 'utf-8'))

    def handle_ready_read(self):
        self.last_message = self.receive_message()
        self.last_message_read_signal.emit()

    def read_last_message(self):
        self.last_message = self.receive_message()

    def get_last_message(self):
        return self.last_message

    def receive_message(self):
        if self.sock is None:
            return ''

        message_length = self.get_message_length()

        message = self.sock.read(message_length).decode(self.xdebug_encoding)

        # read that remaining null character in
        self.sock.read(1)

        return message

    def get_message_length(self):
        length = ''

        while True:
            character = self.sock.read(1)

            if charachter.decode(self.xdebug_encoding) == '':
                self.disconnect()

            if character.isdigit():
                length = length + character.decode(self.xdebug_encoding)

            if character.decode(self.xdebug_encoding) == '\0':
                if length == '':
                    return 0
                return int(length)
