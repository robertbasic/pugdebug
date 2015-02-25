# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import socket

from PyQt5.QtCore import QObject, pyqtSignal

from pugdebug.server import PugdebugServer
from pugdebug.message_parser import PugdebugMessageParser

class PugdebugDebugger(QObject):

    server = None
    parser = None

    last_message = ''

    current_file = ''
    current_line = 0

    transaction_id = 0

    debugging_started_signal = pyqtSignal()
    step_command_signal = pyqtSignal()

    def __init__(self):
        super(PugdebugDebugger, self).__init__()

        self.server = PugdebugServer()
        self.parser = PugdebugMessageParser()

        self.server.init_message_read_signal.connect(self.handle_init_message_read)
        self.server.last_message_read_signal.connect(self.handle_last_message_read)

    def start_debug(self):
        if not self.server.isListening():
            self.server.connect()

    def handle_init_message_read(self):
        self.current_file = self.get_index_file()

        self.debugging_started_signal.emit()

    def handle_last_message_read(self):
        last_message = self.server.get_last_message()
        self.last_message = self.parser.parse_continuation_message(last_message)

        self.step_command_signal.emit()

    def stop_debug(self):
        print('stop')
        self.server.close()

    def run_debug(self):
        print('run')
        command = 'run -i %d' % self.get_transaction_id()
        self.server.command(command)

    def step_over(self):
        print('over')
        command = 'step_over -i %d' % self.get_transaction_id()
        self.server.command(command)

    def step_into(self):
        print('in')
        command = 'step_into -i %d' % self.get_transaction_id()
        self.server.command(command)

    def step_out(self):
        print('out')
        command = 'step_out -i %d' % self.get_transaction_id()
        self.server.command(command)

    def get_init_message(self):
        init_message = self.server.get_init_message()
        init_message = self.parser.parse_init_message(init_message)
        return init_message

    def get_index_file(self):
        init_message = self.get_init_message()
        return init_message['fileuri'].replace('file://', '')

    def get_current_file(self):
        if 'filename' in self.last_message:
            self.current_file = self.last_message['filename'].replace('file://', '')

        if self.current_file == '':
            self.current_file = self.get_index_file()

        return self.current_file

    def get_current_line(self):
        if 'lineno' in self.last_message:
            self.current_line = int(self.last_message['lineno'])

        return self.current_line

    def get_transaction_id(self):
        self.transaction_id += 1
        return self.transaction_id
