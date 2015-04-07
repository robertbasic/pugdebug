# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QObject, pyqtSignal

from pugdebug.server import PugdebugServer


class PugdebugDebugger(QObject):
    server = None

    init_message = None
    step_result = ''

    current_file = ''
    current_line = 0

    debugging_started_signal = pyqtSignal()
    debugging_stopped_signal = pyqtSignal()
    step_command_signal = pyqtSignal()
    got_all_variables_signal = pyqtSignal(object)
    breakpoint_removed_signal = pyqtSignal(int)
    breakpoints_listed_signal = pyqtSignal(type([]))

    def __init__(self):
        """Init the debugger object

        Create a PugdebugServer object used to communicate with xdebug client
        through TCP.

        Connect signals to slots.
        """
        super(PugdebugDebugger, self).__init__()

        self.server = PugdebugServer()

        self.server.server_connected_signal.connect(
            self.handle_server_connected
        )
        self.server.server_stopped_signal.connect(self.handle_server_stopped)
        self.server.server_stepped_signal.connect(self.handle_server_stepped)
        self.server.server_got_variables_signal.connect(
            self.handle_server_got_variables
        )
        self.server.server_set_init_breakpoints_signal.connect(
            self.handle_server_set_breakpoint
        )
        self.server.server_set_breakpoint_signal.connect(
            self.handle_server_set_breakpoint
        )
        self.server.server_removed_breakpoint_signal.connect(
            self.handle_server_removed_breakpoint
        )
        self.server.server_listed_breakpoints_signal.connect(
            self.handle_server_listed_breakpoints
        )

    def cleanup(self):
        """Cleanup debugger when it's done
        """
        if self.server.is_connected():
            self.server.disconnect()

        self.step_result = ''
        self.current_file = ''
        self.current_line = 0

    def is_connected(self):
        return self.server.is_connected()

    def start_debug(self):
        """Start a debugging session

        If the server is not connected, connect it.
        """
        self.server.connect()

    def handle_server_connected(self, init_message):
        """Handle when server gets connected

        Emit a debugging started signal.
        """
        self.init_message = init_message

        self.debugging_started_signal.emit()

    def stop_debug(self):
        """Stop a debugging session
        """
        self.server.stop()

    def handle_server_stopped(self):
        """Handle when server gets disconnected

        Emit a debugging stopped signal.
        """
        self.debugging_stopped_signal.emit()

    def run_debug(self):
        self.server.step_run()

    def step_over(self):
        self.server.step_over()

    def step_into(self):
        self.server.step_into()

    def step_out(self):
        self.server.step_out()

    def handle_server_stepped(self, step_result):
        """Handle when server executes a step command

        Save the result of the step command and emit
        a step command signal.
        """
        self.step_result = step_result
        self.step_command_signal.emit()

    def get_variables(self):
        self.server.get_variables()

    def handle_server_got_variables(self, variables):
        """Handle when server recieves all variables

        Emit a signal with all variables received.
        """
        self.got_all_variables_signal.emit(variables)

    def set_init_breakpoints(self, breakpoints):
        self.server.set_init_breakpoints(breakpoints)

    def set_breakpoint(self, breakpoint):
        self.server.set_breakpoint(breakpoint)

    def handle_server_set_breakpoint(self, successful):
        if successful:
            self.list_breakpoints()

    def remove_breakpoint(self, breakpoint_id):
        self.server.remove_breakpoint(breakpoint_id)

    def handle_server_removed_breakpoint(self, breakpoint_id):
        self.breakpoint_removed_signal.emit(breakpoint_id)

    def list_breakpoints(self):
        self.server.list_breakpoints()

    def handle_server_listed_breakpoints(self, breakpoints):
        self.breakpoints_listed_signal.emit(breakpoints)

    def get_index_file(self):
        if 'fileuri' in self.init_message:
            return self.init_message['fileuri']
        else:
            return None

    def get_current_file(self):
        if 'filename' in self.step_result:
            self.current_file = self.step_result['filename']

        return self.current_file

    def get_current_line(self):
        if 'lineno' in self.step_result:
            self.current_line = int(self.step_result['lineno'])

        return self.current_line

    def is_breaking(self):
        return self.is_status('break')

    def is_stopping(self):
        return self.is_status('stopping')

    def is_stopped(self):
        return self.is_status('stopped')

    def is_status(self, status):
        if ('status' in self.step_result and
                self.step_result['status'] == status):
            return True
        return False
