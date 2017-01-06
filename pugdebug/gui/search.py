# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QDialog, QLineEdit, QVBoxLayout, QFormLayout,
                             QListWidget)

from pugdebug.models.file_search import PugdebugFileSearch
from pugdebug.models.settings import get_setting

class PugdebugFileSearchWindow(QDialog):

    def __init__(self, parent):
        super(PugdebugFileSearchWindow, self).__init__(parent)

        self.parent = parent

        self.setWindowTitle("Search for files ...")

        self.accepted.connect(self.open_file)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.search_files)

        project_root = get_setting('path/project_root')
        self.file_search = PugdebugFileSearch(self, project_root)

        self.setup_layout()

    def setup_layout(self):
        self.file_name = QLineEdit()
        self.file_name.textEdited.connect(self.start_timer)

        self.files = QListWidget()
        self.files.itemActivated.connect(self.file_selected)

        search_layout = QFormLayout()
        search_layout.addRow("Search for:", self.file_name)
        search_layout.addRow(self.files)

        box_layout = QVBoxLayout()
        box_layout.addLayout(search_layout)

        self.setLayout(box_layout)

    def start_timer(self, text):
        self.timer.start(500)

    def search_files(self):
        self.files.clear()
        files = self.file_search.search(self.file_name.text())
        self.files.addItems(files)

    def file_selected(self, item):
        print(item.data(Qt.DisplayRole))

    def open_file(self):
        pass
