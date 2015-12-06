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

    server_stopped_signal = pyqtSignal()
    debugging_started_signal = pyqtSignal()
    debugging_post_start_signal = pyqtSignal()
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

        Create a PugdebugServer objects that listens to new connections
        from xdebug.

        Connect server signals to slots.
        """
        super(PugdebugDebugger, self).__init__()

        self.server = PugdebugServer()

        self.connect_server_signals()

    def connect_server_signals(self):
        """Connect server signals to slots
        """
        self.server.new_connection_established_signal.connect(
            self.handle_new_connection_established
        )
        self.server.server_stopped_signal.connect(
            self.handle_server_stopped
        )
        self.server.server_error_signal.connect(
            self.handle_server_error
        )

    def connect_connection_signals(self, connection):
        """Connect signals for a new connection

        Connect signals that gets emitted when post start commands are done,
        a connection is stopped or detached, when a step command is done,
        when variables are read, when stacktraces are read, when breakpoints
        are set or removed, when breakpoints are read, when expressions are
        evaluated.
        """

        # Stop/detach signals
        connection.post_start_signal.connect(
            self.handle_post_start
        )
        connection.stopped_signal.connect(
            self.handle_stopped
        )
        connection.detached_signal.connect(
            self.handle_stopped
        )

        # Step command signals
        connection.stepped_signal.connect(
            self.handle_stepped
        )

        # Variables signals
        connection.got_variables_signal.connect(
            self.handle_got_variables
        )

        # Stacktraces signals
        connection.got_stacktraces_signal.connect(
            self.handle_got_stacktraces
        )

        # Breakpoints signals
        connection.set_breakpoint_signal.connect(
            self.handle_set_breakpoint
        )
        connection.removed_breakpoint_signal.connect(
            self.handle_removed_breakpoint
        )
        connection.listed_breakpoints_signal.connect(
            self.handle_listed_breakpoints
        )

        # Expressions signals
        connection.expression_evaluated_signal.connect(
            self.handle_expression_evaluated
        )
        connection.expressions_evaluated_signal.connect(
            self.handle_expressions_evaluated
        )

        # Error signals
        connection.connection_error_signal.connect(
            self.handle_connection_error
        )

    def cleanup_current_connection(self):
        """Cleanup the current debugger connection

        If there is an active connection, disconnect from it.

        Clean up attributes.
        """
        if self.is_connected():
            self.current_connection.disconnect()

        self.current_connection = None
        self.step_result = ''
        self.current_file = ''
        self.current_line = 0

    def is_connected(self):
        """Is there an active connection
        """
        return self.current_connection is not None

    def has_pending_connections(self):
        """Are there any pending connections?
        """
        return len(self.connections) > 0

    def start_listening(self):
        """Start listening to new connections
        """
        self.server.start_listening()

    def handle_new_connection_established(self, connection):
        """Handle when the server establishes a new connection

        Connect the signals for the new connection.

        Add it to the queue of connections.

        If there is no active connection, start the new connection.
        """
        connection.load_typemap()

        self.connect_connection_signals(connection)

        self.connections.append(connection)

        if not self.is_connected():
            self.start_debugging_new_connection()

    def start_debugging_new_connection(self):
        """Start a new connection

        Get the first (oldest) connection from the queue, set it's init
        message as the init message for the session, set it as the current
        connection and emit the debugging started signal.
        """
        connection = self.connections.popleft()
        self.init_message = connection.init_message
        self.current_connection = connection

        self.debugging_started_signal.emit()

    def post_start_command(self, post_start_data):
        """Issue a post start command

        After a debugging session is started, set the init breakpoints
        and list the breakpoints.
        """
        self.current_connection.post_start_command(post_start_data)

    def handle_post_start(self):
        """Handle post start command
        """
        self.debugging_post_start_signal.emit()

    def stop_listening(self):
        """Stop listening for new connections

        Clear connections queue, stop debugging the current connection.
        """
        self.connections.clear()
        self.stop_debug()

        self.server.stop_listening()

    def handle_server_stopped(self):
        """Handle when the server stops listening to new connections
        """
        self.server_stopped_signal.emit()

    def stop_debug(self):
        """Stop a debugging session

        If there is an active connection, stop only that one, otherwise
        stop the server from listening to new connections.
        """
        if self.is_stopped():
            self.handle_stopped()
        elif self.is_connected():
            self.current_connection.stop()

    def detach_debug(self):
        """Detach the current connection
        """
        if self.is_connected():
            self.current_connection.detach()

    def handle_stopped(self):
        """Handle when a server stopped signal is received

        If there are pending connections, start a new one.

        Otherwise emit a debugging stopped signal.
        """
        if self.has_pending_connections():
            self.start_debugging_new_connection()
        else:
            self.cleanup_current_connection()
            self.debugging_stopped_signal.emit()

    def run_debug(self):
        self.current_connection.step_run()

    def step_over(self):
        self.current_connection.step_over()

    def step_into(self):
        self.current_connection.step_into()

    def step_out(self):
        self.current_connection.step_out()

    def handle_stepped(self, step_result):
        """Handle when server executes a step command

        Save the result of the step command and emit
        a step command signal.
        """
        self.step_result = step_result
        self.step_command_signal.emit()

    def post_step_command(self, post_step_data):
        self.current_connection.post_step_command(post_step_data)

    def handle_got_variables(self, variables):
        """Handle when server recieves all variables

        Emit a signal with all variables received.
        """
        self.got_all_variables_signal.emit(variables)

    def handle_got_stacktraces(self, stacktraces):
        """Handle when server receives stacktraces

        Emit a signal with the stacktraces.
        """
        self.got_stacktraces_signal.emit(stacktraces)

    def set_breakpoint(self, breakpoint):
        self.current_connection.set_breakpoint(breakpoint)

    def handle_set_breakpoint(self, successful):
        if successful:
            self.list_breakpoints()

    def remove_breakpoint(self, breakpoint_id):
        self.current_connection.remove_breakpoint(breakpoint_id)

    def handle_removed_breakpoint(self, breakpoint_id):
        self.breakpoint_removed_signal.emit(breakpoint_id)

    def list_breakpoints(self):
        self.current_connection.list_breakpoints()

    def handle_listed_breakpoints(self, breakpoints):
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

    def handle_expression_evaluated(self, index, result):
        """Handle when server evaluates an expression"""
        self.expression_evaluated_signal.emit(index, result)

    def handle_expressions_evaluated(self, results):
        """Handle when server evaluates a list of expressions"""
        self.expressions_evaluated_signal.emit(results)

    def set_debugger_features(self):
        self.current_connection.set_debugger_features()

    def handle_server_error(self, error):
        """Handle when an error occurs in the server
        """
        self.error_signal.emit(error)

    def handle_connection_error(self, action, error):
        """Handle when an error occurs in the connection

        Kill the current connection and stop debugging.
        """
        # The current connection is FUBAR so just set it to None
        self.current_connection = None
        self.stop_debug()
        self.debugging_stopped_signal.emit()

        error = error + " during %s action" % action
        self.error_signal.emit(error)

        if self.has_pending_connections():
            self.start_debugging_new_connection()

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
