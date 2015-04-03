# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import math

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QPlainTextEdit, QGridLayout, QFrame, QWidget, QTextEdit
from PyQt5.QtGui import QTextCursor, QTextOption, QTextFormat, QColor

class PugdebugDocumentViewer(QTabWidget):

    tabs = {}

    def __init__(self):
        super(PugdebugDocumentViewer, self).__init__()

        self.setTabsClosable(True)

    def add_tab(self, document_widget, filename, path):
        # PugdebugTabContents is a temporary (?!) widget
        # so we can show line numbers by the contents
        # ugly hack, will rewrite post-launch
        #tab_widget = PugdebugTabContents(document_widget)
        tab_index = self.addTab(document_widget, filename)
        self.setCurrentIndex(tab_index)

        self.tabs[tab_index] = path

    def close_tab(self, tab_index):
        self.removeTab(tab_index)

        self.tabs.pop(tab_index, None)

        tabs = {}

        # Reindex the tabs
        number_of_tabs = len(self.tabs)
        if number_of_tabs > 0:
            for index in range(0, number_of_tabs):
                document_widget = self.widget(index)
                tabs[index] = document_widget.get_path()

        self.tabs = tabs

    def focus_tab(self, path):
        tab_index = self.find_tab_index_by_path(path)
        if tab_index is not None:
            self.setCurrentIndex(tab_index)

    def find_tab_index_by_path(self, path):
        tab_index = None
        for i, p in self.tabs.items():
            if p == path:
                tab_index = i
        return tab_index

    def get_current_document(self):
        index = self.currentIndex()
        return self.widget(index)

    def get_document(self, index):
        return self.widget(index)

    def get_document_by_path(self, path):
        index = self.find_tab_index_by_path(path)
        return self.widget(index)

class PugdebugTabContents(QWidget):

    document_widget = None

    def __init__(self, document_widget):
        super(PugdebugTabContents, self).__init__()

        self.document_widget = document_widget

        self.numbers_widget = QPlainTextEdit(self)
        self.numbers_widget.setMaximumWidth(15)
        self.numbers_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.numbers_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.numbers_widget.setFrameShape(QFrame.StyledPanel)
        self.numbers_widget.setFrameShadow(QFrame.Plain)
        self.numbers_widget.setEnabled(False)

        self.document_widget.updateRequest.connect(self.scroll_numbers)

        layout = QGridLayout(self)
        layout.addWidget(self.numbers_widget, 0, 0, 1, 1)
        layout.addWidget(document_widget, 0, 1, 1, 1)

        self.set_numbers()

    def set_numbers(self):
        self.numbers_widget.clear()
        number_of_lines = self.document_widget.blockCount()

        self.set_numbers_width(number_of_lines)

        for line in range(1, number_of_lines + 1):
            self.numbers_widget.appendPlainText("%d" % line)

        self.numbers_widget.moveCursor(QTextCursor.Start)
        self.numbers_widget.setWordWrapMode(QTextOption.NoWrap)

    def set_numbers_width(self, number_of_lines):
        digits = int(math.log10(number_of_lines) + 1)
        width = digits * 10
        self.numbers_widget.setMaximumWidth(width)

    def scroll_numbers(self, rect, dy):
        if (dy != 0):
            m = self.document_widget.verticalScrollBar().value()
            self.numbers_widget.verticalScrollBar().setValue(m)

    def highlight_breakpoint_line(self, line_number):
        line_number = int(line_number) - 1

        ex = self.numbers_widget.extraSelections()

        selection = QTextEdit.ExtraSelection()

        cursor = self.numbers_widget.textCursor()
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number)

        color = QColor(220, 236, 209)

        selection.format.setBackground(color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = cursor

        selection.cursor.clearSelection()

        ex.append(selection)
        self.numbers_widget.setExtraSelections(ex)

    def remove_breakpoint_line(self, line_number):
        line_number = int(line_number) - 1

        ex = []

        extraSelections = self.numbers_widget.extraSelections()

        for extraSelection in extraSelections:
            cursor = extraSelection.cursor
            if cursor.blockNumber() != line_number:
                ex.append(extraSelection)

        self.numbers_widget.setExtraSelections(ex)
