# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class PugdebugFileViewer(QTextEdit):

    def __init__(self):
        super(PugdebugFileViewer, self).__init__()
        self.setText('file viewer')


class PugdebugVariableViewer(QTextEdit):

    def __init__(self):
        super(PugdebugVariableViewer, self).__init__()
        self.setText('var viewer')

class PugdebugStacktraceViewer(QTextEdit):

    def __init__(self):
        super(PugdebugStacktraceViewer, self).__init__()
        self.setText('st viewer')


class PugdebugBreakpointViewer(QTextEdit):

    def __init__(self):
        super(PugdebugBreakpointViewer, self).__init__()
        self.setText('bp viewer')
