# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from base64 import b64encode
import socket

from PyQt5.QtCore import QThread, QMutex, pyqtSignal

from pugdebug.message_parser import PugdebugMessageParser
from pugdebug.models.settings import get_setting


class PugdebugServer(QThread):
    mutex = None

    wait_for_accept = True

    new_connection_established_signal = pyqtSignal(object)
    server_stopped_signal = pyqtSignal()

    server_error_signal = pyqtSignal(str)

    def __init__(self):
        super(PugdebugServer, self).__init__()

        self.mutex = QMutex()

    def run(self):
        self.mutex.lock()

        socket_server = self.__connect()

        if socket_server is not None:
            self.__listen(socket_server)

        self.mutex.unlock()

    def start_listening(self):
        self.wait_for_accept = True
        self.start()

    def stop_listening(self):
        self.wait_for_accept = False

    def __connect(self):
        """Connect to the socket server
        """
        try:
            socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_server.settimeout(1)
        except OSError as e:
            socket_server = None
            self.server_error_signal.emit(e.strerror)

        return socket_server

    def __listen(self, socket_server):
        """Listen to new incomming connections

        For every accepted connection, see if it is valid and emit a signal
        with that new connection.

        Otherwise silently disregard that connection.
        """
        host = get_setting('debugger/host')
        port_number = int(get_setting('debugger/port_number'))

        try:
            socket_server.bind((host, port_number))
            socket_server.listen(5)

            while self.wait_for_accept:
                try:
                    sock, address = socket_server.accept()
                    sock.settimeout(None)

                    if sock is not None:
                        connection = PugdebugServerConnection(sock)
                        is_valid = connection.init_connection()

                        if is_valid:
                            self.new_connection_established_signal.emit(
                                connection
                            )
                        else:
                            connection.disconnect()
                except socket.timeout:
                    pass

        except OSError as e:
            self.server_error_signal.emit(e.strerror)
        finally:
            socket_server.close()

        if not self.wait_for_accept:
            self.server_stopped_signal.emit()


class PugdebugServerConnection(QThread):

    socket = None

    mutex = None

    parser = None

    action = None
    data = None

    is_valid = False
    init_message = None

    transaction_id = 0

    xdebug_encoding = 'iso-8859-1'

    post_start_signal = pyqtSignal()
    stopped_signal = pyqtSignal()
    detached_signal = pyqtSignal()
    stepped_signal = pyqtSignal(dict)
    got_variables_signal = pyqtSignal(object)
    got_stacktraces_signal = pyqtSignal(object)
    set_breakpoint_signal = pyqtSignal(bool)
    removed_breakpoint_signal = pyqtSignal(object)
    listed_breakpoints_signal = pyqtSignal(list)
    expression_evaluated_signal = pyqtSignal(int, dict)
    expressions_evaluated_signal = pyqtSignal(list)

    connection_error_signal = pyqtSignal(str, str)

    def __init__(self, socket):
        super(PugdebugServerConnection, self).__init__()

        self.socket = socket

        self.mutex = QMutex()

        self.parser = PugdebugMessageParser()

    def init_connection(self):
        """Init a new connection

        Read in the init message from xdebug and decide based on the
        idekey should this connection be accepted or not.

        Do note that it is not needed to call it from a new thread, as
        it is already called from a thread separate from the main application
        thread and thus should not block the main thread.
        """
        idekey = get_setting('debugger/idekey')

        response = self.__receive_message()

        init_message = self.parser.parse_init_message(response)

        # See if the init message from xdebug is meant for us
        if idekey != '' and init_message['idekey'] != idekey:
            return False

        self.init_message = init_message

        return True

    def run(self):
        self.mutex.lock()

        data = self.data
        action = self.action

        try:
            if action == 'post_start':
                response = self.__post_start(data)

                self.listed_breakpoints_signal.emit(
                    response['breakpoints']
                )
                self.post_start_signal.emit()
            elif action == 'stop':
                response = self.__stop()
                self.stopped_signal.emit()
            elif action == 'detach':
                response = self.__detach()
                self.detached_signal.emit()
            elif action == 'step_run':
                response = self.__step_run()
                self.stepped_signal.emit(response)
            elif action == 'step_into':
                response = self.__step_into()
                self.stepped_signal.emit(response)
            elif action == 'step_over':
                response = self.__step_over()
                self.stepped_signal.emit(response)
            elif action == 'step_out':
                response = self.__step_out()
                self.stepped_signal.emit(response)
            elif action == 'post_step':
                response = self.__post_step(data)

                self.got_variables_signal.emit(response['variables'])
                self.got_stacktraces_signal.emit(response['stacktraces'])
                self.expressions_evaluated_signal.emit(
                    response['expressions']
                )
            elif action == 'breakpoint_set':
                response = self.__set_breakpoint(data)
                self.set_breakpoint_signal.emit(response)
            elif action == 'breakpoint_remove':
                response = self.__remove_breakpoint(data)
                self.removed_breakpoint_signal.emit(response)
            elif action == 'breakpoint_list':
                response = self.__list_breakpoints()
                self.listed_breakpoints_signal.emit(response)
            elif action == 'evaluate_expression':
                (index, expression) = data
                response = self.__evaluate_expression(expression)
                self.expression_evaluated_signal.emit(index, response)
            elif action == 'set_debugger_features':
                self.__set_debugger_features()
        except OSError as error:
            self.disconnect()
            self.connection_error_signal.emit(action, error.strerror)

        self.mutex.unlock()

    def disconnect(self):
        if self.socket is not None:
            self.socket.close()

    def post_start_command(self, post_start_data):
        self.data = post_start_data
        self.action = 'post_start'
        self.start()

    def stop(self):
        self.action = 'stop'
        self.start()

    def detach(self):
        self.action = 'detach'
        self.start()

    def step_run(self):
        self.action = 'step_run'
        self.start()

    def step_into(self):
        self.action = 'step_into'
        self.start()

    def step_over(self):
        self.action = 'step_over'
        self.start()

    def step_out(self):
        self.action = 'step_out'
        self.start()

    def post_step_command(self, post_step_data):
        self.data = post_step_data
        self.action = 'post_step'
        self.start()

    def set_breakpoint(self, breakpoint):
        self.action = 'breakpoint_set'
        self.data = breakpoint
        self.start()

    def remove_breakpoint(self, breakpoint_id):
        self.action = 'breakpoint_remove'
        self.data = breakpoint_id
        self.start()

    def list_breakpoints(self):
        self.action = 'breakpoint_list'
        self.start()

    def evaluate_expression(self, index, expression):
        self.action = 'evaluate_expression'
        self.data = (index, expression)
        self.start()

    def set_debugger_features(self):
        self.action = 'set_debugger_features'
        self.start()

    def __post_start(self, data):
        post_start_response = {
            'debugger_features': self.__set_debugger_features(),
            'init_breakpoints': self.__set_init_breakpoints(
                data['init_breakpoints']
            ),
            'breakpoints': self.__list_breakpoints()
        }

        return post_start_response

    def __stop(self):
        command = 'stop -i %d' % self.__get_transaction_id()
        self.__send_command(command)

        return True

    def __detach(self):
        command = 'detach -i %d' % self.__get_transaction_id()
        self.__send_command(command)

        return True

    def __step_run(self):
        command = 'run -i %d' % self.__get_transaction_id()
        return self.__do_step_command(command)

    def __step_into(self):
        command = 'step_into -i %d' % self.__get_transaction_id()
        return self.__do_step_command(command)

    def __step_over(self):
        command = 'step_over -i %d' % self.__get_transaction_id()
        return self.__do_step_command(command)

    def __step_out(self):
        command = 'step_out -i %d' % self.__get_transaction_id()
        return self.__do_step_command(command)

    def __do_step_command(self, command):
        response = self.__send_command(command)

        response = self.parser.parse_continuation_message(response)

        return response

    def __post_step(self, data):
        post_step_response = {
            'variables': self.__get_variables(),
            'stacktraces': self.__get_stacktraces(),
            'expressions': self.__evaluate_expressions(data['expressions'])
        }

        return post_step_response

    def __get_variables(self):
        command = 'context_names -i %d' % self.__get_transaction_id()
        response = self.__send_command(command)

        contexts = self.parser.parse_variable_contexts_message(response)

        variables = {}

        for context in contexts:
            context_id = int(context['id'])
            command = 'context_get -i %d -c %d' % (
                self.__get_transaction_id(),
                context_id
            )
            response = self.__send_command(command)

            var = self.parser.parse_variables_message(response)
            variables[context['name']] = var

        return variables

    def __get_stacktraces(self):
        command = 'stack_get -i %d' % self.__get_transaction_id()
        response = self.__send_command(command)

        stacktraces = self.parser.parse_stacktraces_message(response)

        return stacktraces

    def __set_init_breakpoints(self, breakpoints):
        all_successful = True

        for breakpoint in breakpoints:
            response = self.__set_breakpoint(breakpoint)
            if response is False:
                all_successful = False

        return all_successful

    def __set_breakpoint(self, breakpoint):
        command = 'breakpoint_set -i %d -t %s -f %s -n %d' % (
            self.__get_transaction_id(),
            'line',
            breakpoint['filename'],
            int(breakpoint['lineno'])
        )
        response = self.__send_command(command)

        return self.parser.parse_breakpoint_set_message(response)

    def __remove_breakpoint(self, breakpoint_id):
        command = 'breakpoint_remove -i %d -d %d' % (
            self.__get_transaction_id(),
            breakpoint_id
        )
        response = self.__send_command(command)

        return self.parser.parse_breakpoint_remove_message(response)

    def __list_breakpoints(self):
        command = 'breakpoint_list -i %d' % self.__get_transaction_id()
        response = self.__send_command(command)

        breakpoints = self.parser.parse_breakpoint_list_message(response)

        return breakpoints

    def __evaluate_expressions(self, expressions):
        results = []
        for index, expression in enumerate(expressions):
            results.append(
                self.__evaluate_expression(expression)
            )

        return results

    def __evaluate_expression(self, expression):
        tid = self.__get_transaction_id()
        b64 = b64encode(bytes(expression, 'UTF-8')).decode()
        command = 'eval -i %d -- %s' % (tid, b64)
        response = self.__send_command(command)

        return self.parser.parse_eval_message(response)

    def __set_debugger_features(self):
        max_depth = int(get_setting('debugger/max_depth'))
        command = 'feature_set -i %d -n max_depth -v %d' % (
            self.__get_transaction_id(),
            max_depth
        )
        response = self.__send_command(command)

        max_children = int(get_setting('debugger/max_children'))
        command = 'feature_set -i %d -n max_children -v %d' % (
            self.__get_transaction_id(),
            max_children
        )
        response = self.__send_command(command)

        max_data = int(get_setting('debugger/max_data'))
        command = 'feature_set -i %d -n max_data -v %d' % (
            self.__get_transaction_id(),
            max_data
        )
        response = self.__send_command(command)

        return True

    def __send_command(self, command):
        self.socket.send(bytes(command + '\0', 'utf-8'))
        return self.__receive_message()

    def __receive_message(self):
        length = self.__get_message_length()
        body = self.__get_message_body(length)

        return body

    def __get_message_length(self):
        length = ''

        while True:
            character = self.socket.recv(1)

            if self.__is_eof(character):
                self.disconnect()

            if character.isdigit():
                length = length + character.decode(self.xdebug_encoding)

            if character.decode(self.xdebug_encoding) == '\0':
                if length == '':
                    return 0
                return int(length)

    def __get_message_body(self, length):
        body = ''

        while length > 0:
            data = self.socket.recv(length)

            if self.__is_eof(data):
                self.disconnect()

            body = body + data.decode(self.xdebug_encoding)

            length = length - len(data)

        self.__get_null()

        return body

    def __get_null(self):
        while True:
            character = self.socket.recv(1)

            if self.__is_eof(character):
                self.disconnect()

            if character.decode(self.xdebug_encoding) == '\0':
                return

    def __is_eof(self, data):
        return data.decode(self.xdebug_encoding) == ''

    def __get_transaction_id(self):
        self.transaction_id += 1
        return self.transaction_id
