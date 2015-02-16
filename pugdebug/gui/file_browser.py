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

from pugdebug.models.file_browser import PugdebugFileBrowser

class PugdebugFileBrowserWindow(QWidget):

    def __init__(self, parent):
        super(PugdebugFileBrowserWindow, self).__init__(parent)

        model = PugdebugFileBrowser()

        self.tree = QTreeView(self)

        self.tree.setModel(model)
        self.tree.setRootIndex(model.start_index)

        self.setup_looks()

    def setup_looks(self):
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.tree, 0, 0, 1, 1)

        self.setMaximumWidth(300)

        font = QFont('mono')
        font.setStyleHint(QFont.Monospace)
        font.setPixelSize(12)
        self.tree.setFont(font)

        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
