# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import base64
from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QDialog,
                             QTextEdit, QGridLayout)


class PugdebugVariableViewer(QTreeWidget):

    def __init__(self):
        super(PugdebugVariableViewer, self).__init__()

        self.setColumnCount(3)
        self.setHeaderLabels(['Name', 'Type', 'Value'])

        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 150)

        self.itemDoubleClicked.connect(
            self.handle_variable_double_clicked
        )

    def handle_variable_double_clicked(self, item):
        """Handle when a variable is double clicked

        If the double clicked item is of string type
        show it in a dialog. Allows to inspect long
        strings more easier.
        """
        if item.text(1).find('string') > -1:
            PugdebugVariableDetails(self, item)

    def set_variables(self, variables):
        self.clear()

        if 'Locals' in variables:
            for variable in variables['Locals']:
                self.add_variable(variable)

        if 'Superglobals' in variables:
            item = QTreeWidgetItem(['Superglobals', '', ''])
            self.addTopLevelItem(item)
            for variable in variables['Superglobals']:
                self.add_variable(variable, item)

    def add_variable(self, variable, parent=None):
        type = variable['type']
        tooltip = None

        if type == 'uninitialized':
            return

        # Display the class name instead of type for objects
        if type == 'object':
            type = variable['classname']

        if type == 'array':
            type = "%s {%d}" % (type, int(variable['numchildren']))

        if type == 'string':
            type = "%s {%d}" % (type, int(variable['size']))
            tooltip = "Double click to inspect"

        if 'value' in variable:
            value = variable['value']

            if 'encoding' in variable and value is not None:
                value = base64.b64decode(value).decode()

            if value is None:
                value = 'NULL'

            args = [variable['name'], type, value]
        else:
            args = [variable['name'], type, ' ... ']

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

        if tooltip is not None:
            item.setToolTip(2, tooltip)


class PugdebugVariableDetails(QDialog):

    def __init__(self, parent, item):
        """Dialog to inspect variables in more detail

        Show the contents of a variable in a text edit.
        """
        super(PugdebugVariableDetails, self).__init__(parent)

        edit = QTextEdit(item.text(2))

        layout = QGridLayout(self)
        layout.addWidget(edit, 0, 0, 0, 0)

        self.setLayout(layout)

        self.show()
