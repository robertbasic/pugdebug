# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import os
import json

from pygments import highlight
from pygments.lexers import PhpLexer
from pygments.formatter import Formatter

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat


class PugdebugSyntaxer(QSyntaxHighlighter):

    formatter = None
    lexer = None

    document_length = 0

    buffer = 0

    def __init__(self, document):
        super(PugdebugSyntaxer, self).__init__(document)

        self.formatter = PugdebugFormatter()
        self.lexer = PhpLexer()

        self.document_length = self.document().characterCount()
        highlight(self.document().toPlainText(), self.lexer, self.formatter)

    def highlightBlock(self, text):
        block = self.currentBlock()

        position = block.position()

        if position != 0:
            previous_block = block.previous()
            self.buffer += previous_block.length()

        for format in self.formatter.formats:
            start = format['start'] - self.buffer
            end = format['end'] - self.buffer
            self.setFormat(start, end, format['style'])

class PugdebugFormatter(Formatter):

    styles = {}

    formats = []

    def __init__(self):
        super(PugdebugFormatter, self).__init__()

        for token, style in self.style:
            format = QTextCharFormat()

            if style['color']:
                color = QColor('#'+style['color'])
                format.setForeground(color)

            self.styles[token] = format

    def format(self, tokensource, outfile):
        self.formats = []
        start = 0
        for token, value in tokensource:
            length = len(value)
            end = start + length
            format = {
                'start': start,
                'end': end,
                'style': self.styles[token]
            }
            self.formats.append(format)
            start += length
