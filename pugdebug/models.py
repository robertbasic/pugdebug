# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class PugdebugFileBrowser(QFileSystemModel):

    def __init__(self):
        super(PugdebugFileBrowser, self).__init__()

        home_path = os.path.expanduser('~')

        self.setRootPath(home_path)

        self.start_index = self.index(home_path)
