# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import (QDialog, QLineEdit, QVBoxLayout, QFormLayout,
                             QListWidget)

class PugdebugFileSearchWindow(QDialog):

    def __init__(self, parent):
        super(PugdebugFileSearchWindow, self).__init__(parent)

        self.parent = parent

        self.setWindowTitle("Search for files ...")

        self.accepted.connect(self.open_file)

        self.setup_layout()

    def setup_layout(self):
        self.file_name = QLineEdit()

        self.files = QListWidget()
        self.files.addItems(['1','2','3','4','5','6'])

        search_layout = QFormLayout()
        search_layout.addRow("Search for:", self.file_name)
        search_layout.addRow(self.files)

        box_layout = QVBoxLayout()
        box_layout.addLayout(search_layout)

        self.setLayout(box_layout)

    def open_file(self):
        pass
