# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal

from pugdebug.server import PugdebugServer


class PugdebugDebugger(QObject):
    server = None

    connections = deque()
    current_connection = None

    init_message = None
    step_result = ''

    current_file = ''
    current_line = 0

    debugging_started_signal = pyqtSignal()
    debugging_stopped_signal = pyqtSignal()
    step_command_signal = pyqtSignal()
    got_all_variables_signal = pyqtSignal(object)
    got_stacktraces_signal = pyqtSignal(object)
    breakpoint_removed_signal = pyqtSignal(int)
    breakpoints_listed_signal = pyqtSignal(list)
    expression_evaluated_signal = pyqtSignal(int, dict)
    expressions_evaluated_signal = pyqtSignal(list)

    error_signal = pyqtSignal(str)

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
        self.server.server_stopped_signal.connect(
            self.handle_server_stopped
        )

    def connect_connection_signals(self, connection):
        connection.server_stopped_signal.connect(
            self.handle_server_stopped
        )
        connection.server_detached_signal.connect(
            self.handle_server_stopped
        )

        connection.server_stepped_signal.connect(
            self.handle_server_stepped
        )

        connection.server_got_variables_signal.connect(
            self.handle_server_got_variables
        )

        connection.server_got_stacktraces_signal.connect(
            self.handle_server_got_stacktraces
        )

        connection.server_set_init_breakpoints_signal.connect(
            self.handle_server_set_breakpoint
        )
        connection.server_set_breakpoint_signal.connect(
            self.handle_server_set_breakpoint
        )
        connection.server_removed_breakpoint_signal.connect(
            self.handle_server_removed_breakpoint
        )
        connection.server_listed_breakpoints_signal.connect(
            self.handle_server_listed_breakpoints
        )

        connection.server_expression_evaluated_signal.connect(
            self.handle_server_expression_evaluated
        )
        connection.server_expressions_evaluated_signal.connect(
            self.handle_server_expressions_evaluated
        )

    def cleanup(self):
        """Cleanup debugger when it's done
        """
        if self.is_connected():
            self.current_connection.disconnect()
            self.connections.clear()

        self.server.stop()

        self.current_connection = None
        self.step_result = ''
        self.current_file = ''
        self.current_line = 0

    def is_connected(self):
        return self.current_connection is not None

    def has_pending_connections(self):
        return len(self.connections) > 0

    def start_debug(self):
        """Start a debugging session

        If the server is not connected, connect it.
        """
        self.server.connect()

    def handle_server_connected(self, connection):
        """Handle when server gets connected

        Emit a debugging started signal.
        """
        self.connect_connection_signals(connection)

        self.connections.append(connection)

        if not self.is_connected():
            self.start_new_connection()

    def start_new_connection(self):
        connection = self.connections.popleft()
        self.init_message = connection.init_message
        self.current_connection = connection

        self.debugging_started_signal.emit()

    def stop_debug(self):
        """Stop a debugging session
        """
        if self.is_connected():
            self.current_connection.stop()
        else:
            self.server.stop()

    def detach_debug(self):
        """Detach a debugging session
        """
        if self.is_connected():
            self.current_connection.detach()

    def handle_server_stopped(self):
        """Handle when server gets disconnected

        Emit a debugging stopped signal.
        """
        if self.has_pending_connections():
            self.start_new_connection()
        else:
            self.cleanup()

            self.debugging_stopped_signal.emit()

    def run_debug(self):
        self.current_connection.step_run()

    def step_over(self):
        self.current_connection.step_over()

    def step_into(self):
        self.current_connection.step_into()

    def step_out(self):
        self.current_connection.step_out()

    def handle_server_stepped(self, step_result):
        """Handle when server executes a step command

        Save the result of the step command and emit
        a step command signal.
        """
        self.step_result = step_result
        self.step_command_signal.emit()

    def post_step_command(self, post_step_data):
        self.current_connection.post_step_command(post_step_data)

    def handle_server_got_variables(self, variables):
        """Handle when server recieves all variables

        Emit a signal with all variables received.
        """
        self.got_all_variables_signal.emit(variables)

    def handle_server_got_stacktraces(self, stacktraces):
        """Handle when server receives stacktraces

        Emit a signal with the stacktraces.
        """
        self.got_stacktraces_signal.emit(stacktraces)

    def set_init_breakpoints(self, breakpoints):
        self.current_connection.set_init_breakpoints(breakpoints)

    def set_breakpoint(self, breakpoint):
        self.current_connection.set_breakpoint(breakpoint)

    def handle_server_set_breakpoint(self, successful):
        if successful:
            self.list_breakpoints()

    def remove_breakpoint(self, breakpoint_id):
        self.current_connection.remove_breakpoint(breakpoint_id)

    def handle_server_removed_breakpoint(self, breakpoint_id):
        self.breakpoint_removed_signal.emit(breakpoint_id)

    def list_breakpoints(self):
        self.current_connection.list_breakpoints()

    def handle_server_listed_breakpoints(self, breakpoints):
        self.breakpoints_listed_signal.emit(breakpoints)

    def get_index_file(self):
        if 'fileuri' in self.init_message:
            return self.init_message['fileuri']
        else:
            return None

    def evaluate_expression(self, index, expression):
        """Evaluates a single expression"""
        self.current_connection.evaluate_expression(index, expression)

    def evaluate_expressions(self, expressions):
        """Evaluates a list of expressions"""
        self.current_connection.evaluate_expressions(expressions)

    def handle_server_expression_evaluated(self, index, result):
        """Handle when server evaluates an expression"""
        self.expression_evaluated_signal.emit(index, result)

    def handle_server_expressions_evaluated(self, results):
        """Handle when server evaluates a list of expressions"""
        self.expressions_evaluated_signal.emit(results)

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
