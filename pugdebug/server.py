# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import socket

from PyQt5.QtCore import QByteArray, pyqtSignal, QThread, QMutex

class PugdebugServer(QThread):

    mutex = None
    action = None
    sock = None

    transaction_id = 0

    last_message = ''

    xdebug_encoding = 'iso-8859-1'

    thread_finished_signal = pyqtSignal(type([]))
    server_connected_signal = pyqtSignal()
    server_stepped_signal = pyqtSignal()
    server_got_variables_signal = pyqtSignal()

    def __init__(self):
        super(PugdebugServer, self).__init__()

        self.mutex = QMutex()
        self.thread_finished_signal.connect(self.handle_thread_finished)

    def run(self):
        self.mutex.lock()

        if self.action == 'connect':
            self.__connect_server()
        elif self.action == 'step_into':
            self.__step_into()
        elif self.action == 'variables':
            self.__get_variables()

        self.thread_finished_signal.emit([])

        self.mutex.unlock()

    def handle_thread_finished(self):
        if self.action == 'connect':
            self.server_connected_signal.emit()
        elif self.action == 'step_into':
            self.server_stepped_signal.emit()
        elif self.action == 'variables':
            self.server_got_variables_signal.emit()

    def connect(self):
        self.action = 'connect'
        self.start()

    def is_connected(self):
        return self.sock is not None

    def disconnect(self):
        self.sock.close()
        self.sock = None

    def step_into(self):
        self.action = 'step_into'
        self.start()

    def get_variables(self):
        self.action = 'variables'
        self.start()

    def __connect_server(self):
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.settimeout(None)

        try:
            socket_server.bind(('', 9000))
            self.__init_connection(socket_server)
        except OSError:
            print(OSError.strerror())
            print("Socket bind failed")
        finally:
            socket_server.close()

    def __init_connection(self, socket_server):
        socket_server.listen(5)

        self.sock, address = socket_server.accept()
        self.sock.settimeout(None)
        message = self.__receive_message()

        comm = 'feature_set -i %d -n max_depth -v 1023' % self.__get_transaction_id()
        self.__command(comm)
        message = self.__receive_message()

        comm = 'feature_set -i %d -n max_children -v -1' % self.__get_transaction_id()
        self.__command(comm)
        message = self.__receive_message()
        comm = 'feature_set -i %d -n max_data -v -1' % self.__get_transaction_id()
        self.__command(comm)
        message = self.__receive_message()

    def __step_into(self):
        comm = 'step_into -i %d' % self.__get_transaction_id()
        self.__command(comm)
        message = self.__receive_message()

    def __get_variables(self):
        comm = 'context_names -i %d' % self.__get_transaction_id()
        self.__command(comm)
        message = self.__receive_message()

        comm = 'context_get -i %d -c 0' % self.__get_transaction_id()
        self.__command(comm)
        message = self.__receive_message()

        comm = 'context_get -i %d -c 1' % self.__get_transaction_id()
        self.__command(comm)
        message = self.__receive_message()

    def __command(self, command):
        self.sock.send(bytes(command + '\0', 'utf-8'))

    def __receive_message(self):
        length = self.__get_message_length()
        body = self.__get_message_body(length)

        return body

    def __get_message_length(self):
        length = ''

        while True:
            character = self.sock.recv(1)

            if self.__is_eof(character):
                self.close()

            if character.isdigit():
                length = length + character.decode(self.xdebug_encoding)

            if character.decode(self.xdebug_encoding) == '\0':
                if length == '':
                    return 0
                return int(length)

    def __get_message_body(self, length):
        body = ''

        while length > 0:
            data = self.sock.recv(length)

            if self.__is_eof(data):
                self.close()

            body = body + data.decode(self.xdebug_encoding)

            length = length - len(data)

        self.__get_null()

        return body

    def __get_null(self):
        while True:
            character = self.sock.recv(1)

            if self.__is_eof(character):
                self.close()

            if character.decode(self.xdebug_encoding) == '\0':
                return

    def __is_eof(self, data):
        return data.decode(self.xdebug_encoding) == ''

    def __get_transaction_id(self):
        self.transaction_id += 1
        return self.transaction_id
