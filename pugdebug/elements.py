# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileSystemModel, QTreeView

class PugdebugFileBrowser(QWidget):

    def __init__(self):
        super(PugdebugFileBrowser, self).__init__()

        tree = QTreeView(self)

        home_path = os.path.expanduser('~')

        self.model = QFileSystemModel()
        self.model.setRootPath(home_path)

        index = self.model.index(home_path)

        tree.setModel(self.model)
        tree.setRootIndex(index)
