# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

class PugdebugVariableViewer(QTreeWidget):

    def __init__(self):
        super(PugdebugVariableViewer, self).__init__()

        self.setColumnCount(3)
        self.setHeaderLabels(['Name','Type','Value'])

        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 150)

    def set_variables(self, variables):
        self.clear()

        for context in variables:
            for variable in context:
                item = QTreeWidgetItem([variable['fullname'], variable['type'], variable['value']])
                self.addTopLevelItem(item)
