# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtWidgets import QWidget, QTreeView
from PyQt5.QtGui import QFont

from pugdebug.models.file_browser import PugdebugFileBrowserModel

class PugdebugFileBrowser(QTreeView):

    def __init__(self):
        super(PugdebugFileBrowser, self).__init__()

        model = PugdebugFileBrowserModel()

        self.setModel(model)
        self.setRootIndex(model.start_index)

        self.setup_looks()

    def setup_looks(self):
        self.setMaximumWidth(300)

        font = QFont('mono')
        font.setStyleHint(QFont.Monospace)
        font.setPixelSize(12)
        self.setFont(font)

        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)
