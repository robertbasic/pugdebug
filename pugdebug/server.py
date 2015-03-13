# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import socket

from PyQt5.QtCore import QThread, QMutex, pyqtSignal

from pugdebug.message_parser import PugdebugMessageParser

class PugdebugServer(QThread):

    mutex = None

    sock = None

    parser = None

    action = None

    transaction_id = 0

    xdebug_encoding = 'iso-8859-1'

    thread_finished_signal = pyqtSignal(type([]))
    server_connected_signal = pyqtSignal(type({}))
    server_stepped_signal = pyqtSignal(type({}))
    server_got_variables_signal = pyqtSignal(object)

    def __init__(self):
        super(PugdebugServer, self).__init__()

        self.mutex = QMutex()
        self.parser = PugdebugMessageParser()

        self.thread_finished_signal.connect(self.handle_thread_finished)

    def run(self):
        self.mutex.lock()

        if self.action == 'connect':
            response = self.__connect_server()
        elif self.action == 'step_into':
            response = self.__step_into()
        elif self.action == 'variables':
            response = self.__get_variables()

        self.thread_finished_signal.emit([response])

        self.mutex.unlock()

    def handle_thread_finished(self, thread_result):
        if self.action == 'connect':
            self.server_connected_signal.emit(thread_result.pop())
        elif self.action == 'step_into':
            self.server_stepped_signal.emit(thread_result.pop())
        elif self.action == 'variables':
            self.server_got_variables_signal.emit(thread_result.pop())

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

        response = None

        try:
            socket_server.bind(('', 9000))
            response = self.__init_connection(socket_server)
        except OSError:
            print(OSError.strerror())
            print("Socket bind failed")
        finally:
            socket_server.close()

        return response

    def __init_connection(self, socket_server):
        socket_server.listen(5)

        self.sock, address = socket_server.accept()
        self.sock.settimeout(None)
        response = self.__receive_message()

        init_message = self.parser.parse_init_message(response)

        comm = 'feature_set -i %d -n max_depth -v 9' % self.__get_transaction_id()
        response = self.__command(comm)

        comm = 'feature_set -i %d -n max_children -v 512' % self.__get_transaction_id()
        response = self.__command(comm)

        comm = 'feature_set -i %d -n max_data -v 4096' % self.__get_transaction_id()
        response = self.__command(comm)

        return init_message

    def __step_into(self):
        comm = 'step_into -i %d' % self.__get_transaction_id()
        response = self.__command(comm)

        response = self.parser.parse_continuation_message(response)

        return response

    def __get_variables(self):
        comm = 'context_names -i %d' % self.__get_transaction_id()
        response = self.__command(comm)

        contexts = self.parser.parse_variable_contexts_message(response)

        variables = {}

        for context in contexts:
            context_id = int(context['id'])
            comm = 'context_get -i %d -c %d' % (self.__get_transaction_id(), context_id)
            response = self.__command(comm)

            var = self.parser.parse_variables_message(response)
            variables[context['name']] = var

        return variables

    def __command(self, command):
        self.sock.send(bytes(command + '\0', 'utf-8'))
        return self.__receive_message()

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
