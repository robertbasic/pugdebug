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
        """Init the debugger object

        Create a PugdebugServer object used to communicate with xdebug client
        through TCP.

        Create a PugdebugMessageParser object used to parse the xml responses
        from xdebug.

        Connect signals to slots.
        """
        super(PugdebugDebugger, self).__init__()

        self.server = PugdebugServer()
        self.parser = PugdebugMessageParser()

        self.server.init_message_read_signal.connect(self.handle_init_message_read)
        self.server.last_message_read_signal.connect(self.handle_last_message_read)

    def start_debug(self):
        """Start a debugging session

        If the server is not connected, connect it.
        """
        if not self.server.isListening():
            self.server.connect()

    def cleanup(self):
        """Cleanup debugger when it's done
        """

        if self.server.isListening():
            self.server.cleanup()
            self.server.close()

        self.last_message = ''
        self.current_file = ''
        self.current_line = 0
        self.transaction_id = 0

    def handle_init_message_read(self):
        """Handle when the init message from xdebug is read

        At this point the server should have established a TCP connection and
        the init message from xdebug client should be received.

        Emit the custom debugging started signal.
        """
        self.debugging_started_signal.emit()

    def handle_last_message_read(self):
        """Handle when the latest message from xdebug is read

        This should be called after a command is sent to xdebug
        and a reply message is read.
        """
        last_message = self.server.get_last_message()
        self.last_message = self.parser.parse_continuation_message(last_message)

        self.step_command_signal.emit()

    def stop_debug(self):
        command = 'stop -i %d' % self.get_transaction_id()
        self.server.command(command)

    def run_debug(self):
        command = 'run -i %d' % self.get_transaction_id()
        self.server.command(command)

    def step_over(self):
        command = 'step_over -i %d' % self.get_transaction_id()
        self.server.command(command)

    def step_into(self):
        command = 'step_into -i %d' % self.get_transaction_id()
        self.server.command(command)

    def step_out(self):
        command = 'step_out -i %d' % self.get_transaction_id()
        self.server.command(command)

    def get_init_message(self):
        init_message = self.server.get_init_message()
        init_message = self.parser.parse_init_message(init_message)
        return init_message

    def get_index_file(self):
        init_message = self.get_init_message()

        if 'fileuri' in init_message:
            return init_message['fileuri'].replace('file://', '')

        return ''

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

    def is_breaking(self):
        return self.is_status('break')

    def is_stopping(self):
        return self.is_status('stopping')

    def is_stopped(self):
        return self.is_status('stopped')

    def is_status(self, status):
        if 'status' in self.last_message and self.last_message['status'] == status:
            return True
        return False

    def get_transaction_id(self):
        self.transaction_id += 1
        return self.transaction_id
