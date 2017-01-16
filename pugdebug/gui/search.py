# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtWidgets import (QDialog, QLineEdit, QVBoxLayout, QFormLayout,
                             QListWidget, QAbstractItemView)

from pugdebug.models.file_search import PugdebugFileSearch
from pugdebug.models.settings import get_setting
from PyQt5.QtGui import QFont


class PugdebugFileSearchWindow(QDialog):

    def __init__(self, parent):
        super(PugdebugFileSearchWindow, self).__init__(parent)

        self.parent = parent

        self.setWindowTitle("Search for files ...")

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.search_files)

        self.setup_layout()

        self.resize(500, 250)

    def exec(self):
        self.project_root = get_setting('path/project_root')
        self.file_search = PugdebugFileSearch(self, self.project_root)
        super(PugdebugFileSearchWindow, self).exec()

    def setup_layout(self):
        self.file_name = PugdebugSearchFileLineEdit(self)
        self.file_name.textEdited.connect(self.start_timer)
        self.file_name.returnPressed.connect(self.select_file)
        self.file_name.up_or_down_pressed_signal.connect(self.select_index)

        self.files = QListWidget()
        self.files.setSelectionMode(QAbstractItemView.SingleSelection)
        self.files.itemActivated.connect(self.file_selected)
        font = QFont()
        font.setPixelSize(14)
        self.files.setFont(font)

        search_layout = QFormLayout()
        search_layout.addRow("Search for:", self.file_name)

        box_layout = QVBoxLayout()
        box_layout.addLayout(search_layout)
        box_layout.addWidget(self.files)

        self.setLayout(box_layout)

    def start_timer(self, text):
        self.timer.start(500)

    def search_files(self):
        self.files.clear()
        files = self.file_search.search(self.file_name.text())
        self.files.addItems(files)
        self.files.setCurrentRow(0)

    def select_file(self):
        selected_item = self.files.currentItem()
        self.file_selected(selected_item)

    def select_index(self, direction):
        current_index = self.files.currentRow()
        next_index = current_index
        max_index = self.files.count() - 1
        if direction == 'up' and current_index > 0:
            next_index = current_index - 1
        elif direction == 'down' and current_index < max_index:
            next_index = current_index + 1
        self.files.setCurrentRow(next_index)

    def file_selected(self, item):
        path = item.data(Qt.DisplayRole)
        full_path = "%s/%s" % (self.project_root, path)
        self.parent.search_file_selected_signal.emit(full_path)
        self.accept()


class PugdebugSearchFileLineEdit(QLineEdit):

    up_or_down_pressed_signal = pyqtSignal(str)

    def __init__(self, parent):
        super(PugdebugSearchFileLineEdit, self).__init__()

    def event(self, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Up:
                self.up_or_down_pressed_signal.emit('up')
            elif event.key() == Qt.Key_Down:
                self.up_or_down_pressed_signal.emit('down')

        return QLineEdit.event(self, event)
