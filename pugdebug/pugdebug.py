# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import sys

from PyQt5.QtWidgets import QApplication
from pugdebug.gui.main_window import PugdebugMainWindow

class Pugdebug(QApplication):

    def __init__(self, argv):
        super(Pugdebug, self).__init__(argv)

        self.main_window = PugdebugMainWindow()

    def run(self):
        self.main_window.showMaximized()
        sys.exit(self.exec_())
