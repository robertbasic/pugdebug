# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class PugdebugStacktraceViewer(QTreeWidget):

    item_double_clicked_signal = pyqtSignal(str, int)

    def __init__(self):
        super(PugdebugStacktraceViewer, self).__init__()

        self.setColumnCount(3)
        self.setHeaderLabels(['File', 'Line', 'Where'])

        self.setColumnWidth(0, 350)
        self.setColumnWidth(1, 100)

        self.itemDoubleClicked.connect(self.handle_item_double_clicked)

    def set_stacktraces(self, stacktraces):
        self.clear()

        for stacktrace in stacktraces:
            args = [
                stacktrace['filename'],
                stacktrace['lineno'],
                stacktrace['where']
            ]
            item = QTreeWidgetItem(args)

            self.addTopLevelItem(item)

    def handle_item_double_clicked(self, item, column):
        file = item.text(0)
        line = int(item.text(1))

        self.item_double_clicked_signal.emit(file, line)
