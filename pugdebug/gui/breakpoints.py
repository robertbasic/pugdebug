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

from pugdebug.models.settings import get_setting


class PugdebugBreakpointViewer(QTreeWidget):

    item_double_clicked_signal = pyqtSignal(str, int)

    def __init__(self):
        super(PugdebugBreakpointViewer, self).__init__()

        self.setColumnCount(2)
        self.setHeaderLabels(['File', 'Line'])

        self.setColumnWidth(0, 350)

        self.itemDoubleClicked.connect(self.handle_item_double_clicked)

    def set_breakpoints(self, breakpoints):
        self.clear()

        for breakpoint in breakpoints:
            filename = self.__cut_filename(breakpoint['filename'])
            args = [filename, str(breakpoint['lineno'])]

            item = QTreeWidgetItem(args)

            self.addTopLevelItem(item)

    def handle_item_double_clicked(self, item, column):
        file = item.text(0)
        line = int(item.text(1))

        self.item_double_clicked_signal.emit(file, line)

    def __cut_filename(self, filename):
        path_map = get_setting('path/path_mapping')
        if len(path_map) > 0:
            filename = filename[len(path_map):]
        else:
            root = get_setting('path/project_root')
            filename = filename[len(root):]
        return "~%s" % filename
