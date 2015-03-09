# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import base64
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
                self.add_variable(variable)

    def add_variable(self, variable, parent=None):
        if variable['type'] == 'uninitialized':
            return

        if 'value' in variable:
            value = variable['value']

            if 'encoding' in variable and value is not None:
                value = base64.b64decode(value).decode()

            if value is None:
                value = 'NULL'

            args = [variable['name'], variable['type'], value]
        else:
            args = [variable['name'], variable['type'], ' ... ']

        if parent is None:
            item = QTreeWidgetItem(args)
        else:
            item = QTreeWidgetItem(parent, args)

        if 'variables' in variable:
            for subvar in variable['variables']:
                self.add_variable(subvar, item)

        if parent is None:
            self.addTopLevelItem(item)
        else:
            parent.addChild(item)
