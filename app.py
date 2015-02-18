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

from PyQt5.QtWidgets import QApplication
from pugdebug.pugdebug import Pugdebug

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pugdebug = Pugdebug()
    pugdebug.run()
    app.exit(app.exec_())
