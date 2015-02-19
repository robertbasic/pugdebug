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

class PugdebugDebugger():

    server = None

    def __init__(self):
        self.server = PugdebugServer()

    def start_debug(self):
        if not self.server.is_connected:
            self.server.connect()

    def stop_debug(self):
        print('stop')

    def step_over(self):
        print('over')

    def step_in(self):
        print('in')

    def step_out(self):
        print('out')
