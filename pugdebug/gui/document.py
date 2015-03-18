# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit
from PyQt5.QtGui import QColor, QTextFormat, QTextCursor

class PugdebugDocument(QPlainTextEdit):

    document_model = None

    def __init__(self, document_model):
        super(PugdebugDocument, self).__init__()

        self.document_model = document_model

        self.setReadOnly(True)

        self.cursorPositionChanged.connect(self.highlight)

        self.appendPlainText(document_model.contents)

        self.move_to_line(0)

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        pass

    def contextMenuEvent(self, event):
        pass

    def move_to_line(self, line):
        line = line - 1
        if line < 0:
            line = 0

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor, 0)

        if line > 0:
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line)

        self.setTextCursor(cursor)

    def highlight(self):
        ex = [QTextEdit.ExtraSelection()]
        selection = QTextEdit.ExtraSelection()

        color = QColor(209, 220, 236)

        selection.format.setBackground(color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()

        selection.cursor.clearSelection()

        ex.append(selection)
        self.setExtraSelections(ex)
