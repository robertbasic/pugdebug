# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import base64

from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QMenu, QWidget, QTreeWidget, QTreeWidgetItem,
                             QAction, QToolBar, QVBoxLayout, QAbstractItemView)

from pugdebug.models.settings import get_setting, set_setting, has_setting


class PugdebugExpressionViewer(QWidget):

    expression_added_signal = pyqtSignal(int, str)
    expression_changed_signal = pyqtSignal(int, str)

    def __init__(self):
        super(PugdebugExpressionViewer, self).__init__()

        # Action for adding a new expression
        self.add_action = QAction(QIcon.fromTheme('list-add'), "&Add", self)
        self.add_action.triggered.connect(self.handle_add_action)

        # Action for deleting selected expressions
        self.delete_action = QAction(
            QIcon.fromTheme('list-remove'),
            "&Delete", self
        )
        self.delete_action.setShortcut(QKeySequence("Del"))
        self.delete_action.triggered.connect(self.handle_delete_action)

        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.addAction(self.add_action)
        self.toolbar.addAction(self.delete_action)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(['Expression', 'Type', 'Value'])
        self.tree.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.tree)
        self.setLayout(layout)

        self.restore_state()

        self.tree.itemChanged.connect(self.handle_item_changed)

    def show_context_menu(self, point):
        # Create the context menu on the tree widget
        context_menu = QMenu(self)

        # Add action is always visible
        context_menu.addAction(self.add_action)

        # If clicked on an row, offer to delete it
        if self.tree.itemAt(point):
            context_menu.addAction(self.delete_action)

        point = self.tree.mapToGlobal(point)
        context_menu.popup(point)

    def add_expression(self, expression):
        item = QTreeWidgetItem([expression, '', ''])
        item.setFlags(
            Qt.ItemIsEnabled |
            Qt.ItemIsEditable |
            Qt.ItemIsSelectable
        )
        self.tree.addTopLevelItem(item)

        #  Emit the signal to evaluate the expression
        index = self.tree.indexOfTopLevelItem(item)
        self.expression_added_signal.emit(index, expression)

    def delete_selected(self):
        """Deletes currently selected items from the tree"""
        for item in self.tree.selectedItems():
            index = self.tree.indexOfTopLevelItem(item)
            self.delete_expression(item)
            self.select_next(index)

    def select_next(self, index):
        """Selects the next item after an item has been deleted"""
        prev_item = self.tree.topLevelItem(index - 1)
        next_item = self.tree.topLevelItem(index)

        if prev_item:
            prev_item.setSelected(True)
        elif next_item:
            next_item.setSelected(True)

    def clear_values(self):
        """Deletes values for all expressions"""
        count = self.tree.topLevelItemCount()
        for index in range(0, count):
            item = self.tree.topLevelItem(index)
            item.setData(1, Qt.DisplayRole, '')
            item.setData(2, Qt.DisplayRole, '')
            item.takeChildren()

    def delete_expression(self, item):
        """Deletes the given item from the tree"""
        index = self.tree.indexOfTopLevelItem(item)
        self.tree.takeTopLevelItem(index)

    def get_expressions(self):
        """Returns a list of expressions which are to be evaluated"""
        expressions = []
        for x in range(0, self.tree.topLevelItemCount()):
            expression = self.tree.topLevelItem(x).text(0)
            expressions.append(expression)

        return expressions

    def set_evaluated(self, index, result):
        """Displays an evaluated expression result"""
        type = self.decode_type(result)
        value = self.decode_value(result)

        item = self.tree.topLevelItem(index)
        item.setText(1, type)
        item.setText(2, value)

        variables = result['variables'] if 'variables' in result else []
        self.set_variables(item, variables)

    def set_variables(self, parent, variables):
        """Display an array of variables for the given parent item"""
        for index, variable in enumerate(variables):
            self.set_variable(parent, index, variable)

        # Delete any children which no longer exist
        # Last displayed index should be len(variables) - 1
        index = len(variables)
        while parent.child(index):
            parent.takeChild(index)

    def set_variable(self, parent, index, variable):
        """Display a single variable within the given parent item"""
        name = variable['name']
        type = self.decode_type(variable)
        value = self.decode_value(variable)

        item = parent.child(index)
        if item is None:
            # Item does not exist, create it
            item = QTreeWidgetItem([name, type, value])
            parent.insertChild(index, item)
        else:
            # Item exists, modify it
            item.setData(0, Qt.DisplayRole, name)
            item.setData(1, Qt.DisplayRole, type)
            item.setData(2, Qt.DisplayRole, value)

        # Recurse (we need to go deeper)
        if 'variables' in variable:
            self.set_variables(item, variable['variables'])

    def decode_type(self, result):
        if 'type' not in result:
            return ''

        # Display the class name instead of type for objects
        if result['type'] == 'object':
            return result['classname']

        return result['type']

    def decode_value(self, result):
        value = None

        if 'value' in result:
            value = result['value']

        if 'encoding' in result and value is not None:
            value = base64.b64decode(value)
            try:
                value = value.decode()
            except:
                value = repr(value)

        if result['type'] == 'bool':
            value = 'false' if value == '0' else 'true'

        return value

    def save_state(self):
        """Save current expressions to settings"""
        set_setting('expressions_viewer/expressions', self.get_expressions())

    def restore_state(self):
        """Load expressions from settings"""
        expressions = []

        if has_setting('expressions_viewer/expressions'):
            expressions = get_setting('expressions_viewer/expressions')

        if expressions is not None:
            for expression in expressions:
                self.add_expression(expression)

    def handle_add_action(self):
        self.add_expression('$x')
        self.save_state()

    def handle_delete_action(self):
        self.delete_selected()
        self.save_state()

    def handle_item_changed(self, item, column):
        """Called when the user changes an item"""

        # Only check top level items
        if item.parent():
            return

        # Only check changes to the first column which contains the expressions
        if column > 0:
            return

        index = self.tree.indexOfTopLevelItem(item)
        expression = item.text(0)

        self.expression_changed_signal.emit(index, expression)
        self.save_state()
