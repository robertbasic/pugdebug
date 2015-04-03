# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import math

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit, QGridLayout
from PyQt5.QtGui import QColor, QTextFormat, QTextCursor, QPainter

from pugdebug.syntaxer import PugdebugSyntaxer


class PugdebugDocument(QWidget):
    """A document widget to display code and line numbers

    This document widget is built from two different widgets, one being
    a QPlainTextEdit widget that holds the contents of the document, and
    the other being a simple QWidget that gets the line numbers painted on.
    """

    document_contents = None

    line_numbers = None

    def __init__(self, document_model, syntaxer_rules):
        super(PugdebugDocument, self).__init__()

        # The QPlainTextEdit widget that holds the contents of the document
        self.document_contents = PugdebugDocumentContents(
            document_model,
            syntaxer_rules
        )

        # The QWidget that gets the line numbers
        self.line_numbers = PugdebugLineNumbers(self)

        self.document_contents.updateRequest.connect(
            self.handle_document_contents_update_request
        )

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.line_numbers, 0, 0, 1, 1)
        self.layout.addWidget(self.document_contents, 0, 1, 1, 1)

    def handle_document_contents_update_request(self, rect, dy):
        """Handle the update request for document contents

        Scroll the line numbers along with the document contents.

        Set the width of the line numbers widget.
        """
        if (dy != 0):
            self.line_numbers.scroll(0, dy)

        number_of_lines = self.document_contents.blockCount()
        self.line_numbers.set_numbers_width(number_of_lines)

    def paint_line_numbers(self, line_numbers, event):
        """Paint the line numbers

        For every visible block in the document draw it's corresponding line
        number in the line numbers widget.
        """
        font_metrics = self.document_contents.fontMetrics()

        painter = QPainter(line_numbers)
        painter.fillRect(event.rect(), self.document_contents.palette().base())

        block = self.document_contents.firstVisibleBlock()
        line_number = block.blockNumber()

        height = font_metrics.height()
        width = line_numbers.width()

        while block.isValid():
            # blocks are numbered from zero
            line_number += 1

            content_offset = self.document_contents.contentOffset()
            # Get the top coordinate of the current block
            # to know where to paint the line number for it
            block_top = (self.document_contents
                             .blockBoundingGeometry(block)
                             .translated(content_offset)
                             .top())

            if not block.isVisible() or block_top >= event.rect().bottom():
                break

            # Convert the line number to string so we can paint it
            text = str(line_number)

            painter.drawText(0, block_top, width, height, Qt.AlignRight, text)

            block = block.next()

        painter.end()


class PugdebugDocumentContents(QPlainTextEdit):

    document_model = None

    syntaxer = None

    document_double_clicked_signal = pyqtSignal(str, int)

    def __init__(self, document_model, syntaxer_rules):
        super(PugdebugDocumentContents, self).__init__()

        self.document_model = document_model

        self.setReadOnly(True)

        self.cursorPositionChanged.connect(self.highlight)

        self.setPlainText(document_model.contents)

        self.move_to_line(0)

        self.syntaxer = PugdebugSyntaxer(self.document(), syntaxer_rules)

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        path = self.document_model.path

        cursor = self.cursorForPosition(event.pos())
        line_number = cursor.blockNumber()
        line_number += 1

        self.document_double_clicked_signal.emit(path, line_number)

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


class PugdebugLineNumbers(QWidget):

    document_widget = None

    def __init__(self, document_widget):
        super(PugdebugLineNumbers, self).__init__()

        self.document_widget = document_widget

    def set_numbers_width(self, number_of_lines):
        digits = int(math.log10(number_of_lines) + 1)
        width = digits * 10
        self.setFixedWidth(width)

    def paintEvent(self, event):
        self.document_widget.paint_line_numbers(self, event)
