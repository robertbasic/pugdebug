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
from pugdebug import gui

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QMainWindow()

    main_window = gui.PugdebugMain(window)

    window.show()

    sys.exit(app.exec_())
