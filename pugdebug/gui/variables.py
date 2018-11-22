# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import base64

from PyQt5.QtWidgets import (QTabWidget, QTreeWidget, QTreeWidgetItem, QDialog,
                             QTextEdit, QGridLayout, QHeaderView)


class PugdebugVariableViewer(QTabWidget):

    variable_tables = {}

    def __init__(self):
        """Variable viewer

        Every variable context is displayed in a table,
        contexts are displayed in tabs.
        """
        super(PugdebugVariableViewer, self).__init__()

        self.setTabsClosable(False)

    def handle_variable_double_clicked(self, item):
        """Handle when a variable is double clicked

        If the double clicked item is of string type
        show it in a dialog. Allows to inspect long
        strings more easier.
        """
        if item.text(1).find('string') > -1:
            PugdebugVariableDetails(self, item)

    def clear(self):
        """Clear the variable tables
        """
        for context_key in self.variable_tables:
            self.variable_tables[context_key].clear()

    def set_variables(self, variables):
        for context in variables:
            table = self.get_variable_table(context)

            table.clear()

            for var in variables[context]:
                self.add_variable(table, var)

    def get_variable_table(self, context):
        context_key = context.replace(' ', '-').lower()

        if context_key in self.variable_tables:
            table = self.variable_tables[context_key]
        else:
            table = QTreeWidget()
            table.setColumnCount(3)
            table.setHeaderLabels(['Name', 'Type', 'Value'])
            table.header().setSectionResizeMode(0, QHeaderView.Stretch)
            table.header().setSectionResizeMode(1, QHeaderView.Stretch)
            table.header().setSectionResizeMode(2, QHeaderView.Stretch)

            self.variable_tables[context_key] = table

            if context == 'Locals':
                self.insertTab(0, table, context)
            else:
                self.addTab(table, context)

            table.itemDoubleClicked.connect(
                self.handle_variable_double_clicked
            )

            self.setCurrentIndex(0)

        return table

    def add_variable(self, table, variable, parent=None):
        type = variable['type']
        tooltip = None

        if type == 'uninitialized':
            return

        # Display the class name instead of type for objects
        if type == 'object':
            type = variable['classname']

        if (type == 'array' or type == 'hash') and 'numchildren' in variable:
            type = "%s {%d}" % (type, int(variable['numchildren']))

        if type == 'string' and 'size' in variable:
            type = "%s {%d}" % (type, int(variable['size']))
            tooltip = "Double click to inspect"

        if 'value' in variable:
            value = variable['value']

            if 'encoding' in variable and value is not None:
                value = base64.b64decode(value)
                try:
                    value = value.decode()
                except:
                    value = repr(value)

            if value is None:
                value = 'NULL'

            if type == 'bool':
                value = ("%s" % (int(value) == 1)).lower()

            args = [variable['name'], type, value]
        else:
            args = [variable['name'], type, ' ... ']

        if parent is None:
            item = QTreeWidgetItem(args)
        else:
            item = QTreeWidgetItem(parent, args)

        if 'variables' in variable:
            for subvar in variable['variables']:
                self.add_variable(table, subvar, item)

        if parent is None:
            table.addTopLevelItem(item)
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
