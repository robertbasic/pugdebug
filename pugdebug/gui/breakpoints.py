# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class PugdebugBreakpointViewer(QTreeWidget):

    def __init__(self):
        super(PugdebugBreakpointViewer, self).__init__()

        self.setColumnCount(2)
        self.setHeaderLabels(['File', 'Line'])

        self.setColumnWidth(0, 350)

    def set_breakpoints(self, breakpoints):
        self.clear()

        for breakpoint in breakpoints:
            args = [breakpoint['filename'], str(breakpoint['lineno'])]

            item = QTreeWidgetItem(args)

            self.addTopLevelItem(item)
