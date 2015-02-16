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

class PugdebugVariableViewer(QTextEdit):

    def __init__(self):
        super(PugdebugVariableViewer, self).__init__()
        self.setText('var viewer')
