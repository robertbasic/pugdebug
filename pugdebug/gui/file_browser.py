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


class PugdebugFileBrowser(QTreeView):

    def __init__(self):
        super(PugdebugFileBrowser, self).__init__()

        self.setup_looks()

    def setup_looks(self):
        self.setMaximumWidth(300)

        font = QFont('mono')
        font.setStyleHint(QFont.Monospace)
        font.setPixelSize(12)
        self.setFont(font)

    def hide_columns(self):
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)
