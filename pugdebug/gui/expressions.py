# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import base64

from PyQt5.QtWidgets import QMenu, QTreeWidget, QTreeWidgetItem, QAction
from PyQt5.QtCore import Qt

from pugdebug.models.settings import get_setting, set_setting, has_setting


class PugdebugExpressionViewer(QTreeWidget):

    def __init__(self):
        super(PugdebugExpressionViewer, self).__init__()
        self.setColumnCount(3)
        self.setHeaderLabels(['Expression', 'Type', 'Value'])

        self.setup_context_menu()
        self.restore_state()
        self.itemChanged.connect(self.handle_item_changed)

    def setup_context_menu(self):
        """Override default context menu"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, point):
        # Create the context menu
        self.context_menu = QMenu(self)
        self.context_menu.addAction("&Add expression", self.add_expression_action)

        # If clicked on an row, offer to delete it
        item = self.itemAt(point)
        if item:
            deleteAction = QAction("&Delete expression", self.context_menu)
            deleteAction.triggered.connect(lambda: self.delete_expression(item))
            self.context_menu.addAction(deleteAction)

        point = self.mapToGlobal(point)
        self.context_menu.popup(point)

    def add_expression_action(self):
        self.add_expression('$x')
        self.save_state()

    def add_expression(self, expression):
        item = QTreeWidgetItem([expression, '', ''])
        item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsEditable)
        self.addTopLevelItem(item)

    def delete_expression(self, item):
        index = self.indexOfTopLevelItem(item)
        self.takeTopLevelItem(index)
        self.save_state()

    def get_expressions(self):
        """Returns a list of expressions which are to be evaluated"""
        expressions = []
        for x in range(0, self.topLevelItemCount()):
            expression = self.topLevelItem(x).text(0)
            expressions.append(expression)

        return expressions

    def set_evaluated(self, results):
        """Displays evaluation results"""
        for key, result in enumerate(results):
            type = result['type'] if 'type' in result else None
            value = self.decode_value(result)

            item = self.topLevelItem(key)
            item.setText(1, type)
            item.setText(2, value)

    def decode_value(self, result):
        value = None

        if 'value' in result:
            value = result['value']

        if 'encoding' in result and value is not None:
            value = base64.b64decode(value).decode()

        return value

    def save_state(self):
        """Save current expressions to settings"""
        set_setting('expressions_viewer/expressions', self.get_expressions())

    def restore_state(self):
        """Load expressions from settings"""
        expressions = []

        if has_setting('expressions_viewer/expressions'):
            expressions = get_setting('expressions_viewer/expressions')

        for expression in expressions:
            self.add_expression(expression)

    def handle_item_changed(self, item, column):
        """If user changed the expression, save the state to settings"""
        if column == 0:
            self.save_state()

