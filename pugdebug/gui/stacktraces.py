# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class PugdebugStacktraceViewer(QTreeWidget):

    def __init__(self):
        super(PugdebugStacktraceViewer, self).__init__()

        self.setColumnCount(3)
        self.setHeaderLabels(['File', 'Line', 'Where'])

        self.setColumnWidth(0, 350)
        self.setColumnWidth(1, 100)

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
