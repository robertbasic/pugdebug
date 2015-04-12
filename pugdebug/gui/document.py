# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import math

from PyQt5.QtCore import pyqtSignal, Qt, QRect
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit, QGridLayout
from PyQt5.QtGui import (QColor, QTextFormat, QTextCursor, QPainter,
                         QTextBlockUserData)

from pugdebug.syntaxer import PugdebugSyntaxer


class PugdebugDocument(QWidget):
    """A document widget to display code and line numbers

    This document widget is built from two different widgets, one being
    a QPlainTextEdit widget that holds the contents of the document, and
    the other being a simple QWidget that gets the line numbers painted on.
    """

    document_contents = None

    line_numbers = None

    document_double_clicked_signal = pyqtSignal(str, int)

    def __init__(self, document_model, syntaxer_rules):
        super(PugdebugDocument, self).__init__()

        # The QPlainTextEdit widget that holds the contents of the document
        self.document_contents = PugdebugDocumentContents(
            self,
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

            if self.document_contents.block_hit_breakpoint(block):
                # If block has hit a breakpoint,
                # draw a red rectangle by the line number
                brush = painter.brush()
                brush.setStyle(Qt.SolidPattern)
                brush.setColor(Qt.red)
                painter.setBrush(brush)
                rect = QRect(0, block_top+2, 7, 7)
                painter.drawRect(rect)
                self.document_contents.block_remove_hit_breakpoint(block)
            elif self.document_contents.block_has_breakpoint(block):
                # If block has a breakpoint,
                # draw a green rectangle by the line number
                brush = painter.brush()
                brush.setStyle(Qt.SolidPattern)
                brush.setColor(Qt.darkGreen)
                painter.setBrush(brush)
                rect = QRect(0, block_top+2, 7, 7)
                painter.drawRect(rect)

            # Convert the line number to string so we can paint it
            text = str(line_number)

            painter.drawText(0, block_top, width, height, Qt.AlignRight, text)

            block = block.next()

        painter.end()

    def get_path(self):
        return self.document_contents.document_model.path

    def move_to_line(self, line):
        self.document_contents.move_to_line(line)

    def breakpoint_hit(self, line):
        """Mark line number as breakpoint hit

        If the line has a breakpoint, mark it as
        the breakpoint is hit.

        Repaint the line numbers.
        """
        self.document_contents.breakpoint_hit(line)
        self.rehighlight_breakpoint_lines()

    def rehighlight_breakpoint_lines(self):
        """Rehighlight breakpoint lines

        Update the line numbers so the paint event gets fired
        and so the breakpoints get repainted as well.
        """
        self.line_numbers.update()


class PugdebugDocumentContents(QPlainTextEdit):

    document_widget = None

    document_model = None

    syntaxer = None

    def __init__(self, document_widget, document_model, syntaxer_rules):
        super(PugdebugDocumentContents, self).__init__()

        self.document_widget = document_widget

        self.document_model = document_model

        self.setReadOnly(True)

        self.cursorPositionChanged.connect(self.highlight)

        self.setPlainText(document_model.contents)

        self.remove_line_highlights()

        self.syntaxer = PugdebugSyntaxer(self.document(), syntaxer_rules)

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        path = self.document_model.path

        cursor = self.cursorForPosition(event.pos())

        block = cursor.block()

        # Do not try to set breakpoints on empty lines
        if len(block.text()) == 0:
            return

        # Set/unset breakpoint flag on the double clicked line
        if self.block_has_breakpoint(block):
            self.block_remove_breakpoint(block)
        else:
            self.block_set_breakpoint(block)

        line_number = block.blockNumber() + 1

        self.document_widget.document_double_clicked_signal.emit(
            path,
            line_number
        )

    def contextMenuEvent(self, event):
        pass

    def move_to_line(self, line):
        """Move cursor to line

        Move the cursor of the QPlainTextEdit that holds the document
        contents to the line.

        Move the cursor block by block until the block number matches
        the line number.
        """
        line = line - 1
        if line < 0:
            line = 0

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor, 0)

        block_number = cursor.blockNumber()
        while block_number < line:
            cursor.movePosition(
                QTextCursor.NextBlock,
                QTextCursor.MoveAnchor,
                1
            )
            block_number = cursor.blockNumber()

        self.setTextCursor(cursor)

    def breakpoint_hit(self, line):
        """Mark line number as breakpoint hit

        If the line has a breakpoint, mark it as
        a breakpoint hit.
        """
        line = line - 1
        if line < 0:
            line = 0

        cursor = self.textCursor()
        block = cursor.block()

        if self.block_has_breakpoint(block):
            self.block_set_hit_breakpoint(block)

    def highlight(self):
        selection = QTextEdit.ExtraSelection()

        color = QColor(209, 220, 236)

        selection.format.setBackground(color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()

        selection.cursor.clearSelection()

        self.setExtraSelections([selection])

    def remove_line_highlights(self):
        """Remove line highlights

        Move the cursor to first (zero) line.

        Clear the extra selections in the file.
        """
        self.move_to_line(0)
        self.setExtraSelections([])

    def block_has_breakpoint(self, block):
        user_data = self.__get_block_user_data(block)
        return user_data.breakpoint

    def block_set_breakpoint(self, block):
        user_data = self.__get_block_user_data(block)
        user_data.breakpoint = True
        block.setUserData(user_data)

    def block_remove_breakpoint(self, block):
        user_data = self.__get_block_user_data(block)
        user_data.breakpoint = False
        block.setUserData(user_data)

    def block_hit_breakpoint(self, block):
        user_data = self.__get_block_user_data(block)
        return user_data.breakpoint_hit

    def block_set_hit_breakpoint(self, block):
        user_data = self.__get_block_user_data(block)
        user_data.breakpoint_hit = True
        block.setUserData(user_data)

    def block_remove_hit_breakpoint(self, block):
        user_data = self.__get_block_user_data(block)
        user_data.breakpoint_hit = False
        block.setUserData(user_data)

    def __get_block_user_data(self, block):
        user_data = block.userData()
        if user_data is None:
            user_data = PugdebugBlockData()
        return user_data


class PugdebugLineNumbers(QWidget):

    document_widget = None

    def __init__(self, document_widget):
        super(PugdebugLineNumbers, self).__init__()

        self.document_widget = document_widget

    def set_numbers_width(self, number_of_lines):
        digits = int(math.log10(number_of_lines) + 1)
        # add 7 to have space to paint the breakpoint markers
        width = digits * 10 + 7
        self.setFixedWidth(width)

    def paintEvent(self, event):
        self.document_widget.paint_line_numbers(self, event)


class PugdebugBlockData(QTextBlockUserData):

    breakpoint = False
    breakpoint_hit = False

    def __init__(self):
        super(PugdebugBlockData, self).__init__()
