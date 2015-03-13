#! python

# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import sys, socket

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Server(QObject):

    thread = None

    server_connected = pyqtSignal()

    def __init__(self):
        super(Server, self).__init__()

        self.thread = Thread()

        self.thread.thread_finished.connect(self.on_thread_finished)

    def connect(self):
        self.thread.action = 'connect'
        self.thread.start()

    def step_into(self):
        self.thread.action = 'step_into'
        self.thread.start()

    def on_thread_finished(self, args):
        print(args)
        if self.thread.action == 'connect':
            self.server_connected.emit()
        elif self.thread.action == 'step_into':
            print('done stepping into')

class Thread(QThread):

    mutex = None

    action = None

    sock = None

    xdebug_encoding = 'iso-8859-1'

    thread_finished = pyqtSignal(type([]))

    tid = 0

    def __init__(self):
        super(Thread, self).__init__()

        self.mutex = QMutex()

    def get_tid(self):
        self.tid += 1
        return self.tid

    def run(self):
        self.mutex.lock()

        if self.action == 'connect':
            self.__connect_server()
        elif self.action == 'step_into':
            self.__step_into()

        self.thread_finished.emit(['some', 'data'])

        self.mutex.unlock()

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

    def __step_into(self):
        comm = 'step_into -i %d' % self.get_tid()
        self.__command(comm)
        message = self.__receive_message()
        print(message)

        comm = 'context_names -i %d' % self.get_tid()
        self.__command(comm)
        message = self.__receive_message()
        print(message)

        comm = 'context_get -i %d -c 0' % self.get_tid()
        self.__command(comm)
        message = self.__receive_message()
        print(message)

        comm = 'context_get -i %d -c 1' % self.get_tid()
        self.__command(comm)
        message = self.__receive_message()
        print(message)

    def __init_connection(self, socket_server):
        socket_server.listen(5)

        print('Waiting for connection ...')

        self.sock, address = socket_server.accept()
        self.sock.settimeout(None)
        message = self.__receive_message()

        comm = 'feature_set -i %d -n max_depth -v 1023' % self.get_tid()
        self.__command(comm)
        message = self.__receive_message()

        comm = 'feature_set -i %d -n max_children -v -1' % self.get_tid()
        self.__command(comm)
        message = self.__receive_message()
        comm = 'feature_set -i %d -n max_data -v -1' % self.get_tid()
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


class Debugger(QObject):

    server = None

    debugging_started = pyqtSignal()
    debugging_stopped = pyqtSignal()
    stepped_into = pyqtSignal()

    def __init__(self):
        super(Debugger, self).__init__()

        self.server = Server()

        self.server.server_connected.connect(self.on_server_connected)

    def connect_server(self):
        self.server.connect()

    def start_debugging(self):
        self.connect_server()

    def on_server_connected(self):
        self.debugging_started.emit()

    def step_into(self):
        self.server.step_into()

class Pugdebug(QMainWindow):

    debugger = None

    def __init__(self):
        super(Pugdebug, self).__init__()

        self.debugger = Debugger()

        toolbar = QToolBar()

        self.start_debug_action = toolbar.addAction("Start")
        self.stop_debug_action = toolbar.addAction("Stop")
        self.step_into_action = toolbar.addAction("In")

        self.start_debug_action.triggered.connect(self.start_debug)
        self.stop_debug_action.triggered.connect(self.stop_debug)
        self.step_into_action.triggered.connect(self.step_into)

        self.addToolBar(toolbar)

        self.show()

        self.debugger.debugging_started.connect(self.on_debugging_started)
        self.debugger.debugging_stopped.connect(self.on_debugging_stopped)
        self.debugger.stepped_into.connect(self.on_stepped_into)

    def start_debug(self):
        self.debugger.start_debugging()

    def on_debugging_started(self):
        self.step_into()

    def stop_debug(self):
        pass

    def on_debugging_stopped(self):
        pass

    def step_into(self):
        self.debugger.step_into()

    def on_stepped_into(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pugdebug = Pugdebug()
    app.exit(app.exec_())
