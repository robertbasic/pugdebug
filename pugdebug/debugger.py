# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import socket

from pugdebug.server import PugdebugServer
from pugdebug.message_parser import PugdebugMessageParser

class PugdebugDebugger():

    server = None
    parser = None

    transaction_id = 0

    def __init__(self):
        self.server = PugdebugServer()
        self.parser = PugdebugMessageParser()

    def start_debug(self):
        if not self.server.is_connected:
            self.server.connect()

    def stop_debug(self):
        print('stop')
        self.server.close()

    def step_over(self):
        print('over')

    def step_in(self):
        print('in')
        command = 'step_into -i %d' % self.get_transaction_id()
        self.server.command(command)

    def step_out(self):
        print('out')

    def get_init_message(self):
        init_message = self.server.get_init_message()
        init_message = self.parser.parse_init_message(init_message)
        return init_message

    def get_index_file(self):
        init_message = self.get_init_message()
        return init_message['fileuri'].replace('file://', '')

    def get_transaction_id(self):
        self.transaction_id += 1
        return self.transaction_id
