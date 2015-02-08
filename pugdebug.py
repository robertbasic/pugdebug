#! python

# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from pugdebug.gui import PugdebugMainWindow

class Pugdebug():

    def __init__(self, argv):
        self.app = QApplication(argv)

        self.main_window = PugdebugMainWindow()

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    pugdebug = Pugdebug(sys.argv)
    pugdebug.run()
