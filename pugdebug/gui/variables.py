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

    def clear_variables(self):
        """Clear all the variables from the tree

        Calling self.clear() should do the same thing
        but it has a delay, it probably works with signals/slots
        so adding variables right after clear might work out of order.
        """
        root = self.invisibleRootItem()
        root.takeChildren()

    def set_variables(self, variables):
        self.clear_variables()

        for context in variables:
            for variable in context:
                if variable['type'] != 'uninitialized':
                    item = QTreeWidgetItem([variable['fullname'], variable['type'], variable['value']])
                    self.addTopLevelItem(item)
