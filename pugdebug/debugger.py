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

    is_session_active = False

    last_command = None

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

        self.server.last_message_read_signal.connect(self.handle_last_message_read)

    def cleanup(self):
        """Cleanup debugger when it's done
        """

        if self.server.isListening():
            self.server.cleanup()
            self.server.close()

        self.last_command = None
        self.last_message = ''
        self.current_file = ''
        self.current_line = 0
        self.transaction_id = 0

        self.is_session_active = False

    def handle_last_message_read(self):
        """Handle when the latest message from xdebug is read

        This should be called after a command is sent to xdebug
        and a reply message is read.
        """

        if self.last_command == 'init':
            self.handle_init_command()
        elif self.last_command == 'continuation':
            self.handle_continuation_command()
        elif self.last_command == 'variable_contexts':
            self.handle_variable_contexts_command()
        elif self.last_command == 'variables':
            self.handle_variables_command()

    def handle_init_command(self):
        """Handle when the init message from xdebug is read

        At this point the server should have established a TCP connection and
        the init message from xdebug client should be received.

        Emit the custom debugging started signal.
        """
        self.is_session_active = True
        self.debugging_started_signal.emit()

    def handle_continuation_command(self):
        last_message = self.server.get_last_message()
        self.last_message = self.parser.parse_continuation_message(last_message)

        self.step_command_signal.emit()

    def handle_variable_contexts_command(self):
        last_message = self.server.get_last_message()
        last_message = self.parser.parse_variable_contexts_message(last_message)

        for context in last_message:
            context_id = int(context['id'])
            self.get_variable_context(context_id)

    def handle_variables_command(self):
        last_message = self.server.get_last_message()
        last_message = self.parser.parse_variables_message(last_message)

        print(last_message)

    def start_debug(self):
        """Start a debugging session

        If the server is not connected, connect it.
        """
        if not self.server.isListening():
            self.last_command = 'init'
            self.server.connect()

    def stop_debug(self):
        command = 'stop'
        self.do_continuation_command(command)

    def run_debug(self):
        command = 'run'
        self.do_continuation_command(command)

    def step_over(self):
        command = 'step_over'
        self.do_continuation_command(command)

    def step_into(self):
        command = 'step_into'
        self.do_continuation_command(command)

    def step_out(self):
        command = 'step_out'
        self.do_continuation_command(command)

    def do_continuation_command(self, command):
        self.last_command = 'continuation'
        command = '%s -i %d' % (command, self.get_transaction_id())
        self.server.command(command)

    def get_all_variables(self):
        self.get_variable_contexts()

    def get_variable_contexts(self):
        self.last_command = 'variable_contexts'
        command = 'context_names -i %d' % self.get_transaction_id()
        self.server.command(command)

    def get_variable_context(self, context_id):
        self.last_command = 'variables'
        command = 'context_get -c %d -i %d' % (context_id, self.get_transaction_id())
        self.server.command(command)

    def get_current_file(self):
        if 'filename' in self.last_message:
            self.current_file = self.last_message['filename'].replace('file://', '')

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
