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

    def __init__(self, document):
        super(PugdebugSyntaxer, self).__init__(document)

        self.formatter = PugdebugFormatter()
        self.lexer = PhpLexer()

    def highlightBlock(self, text):
        position = self.currentBlock().position()

        text = self.document().toPlainText()

        highlight(text, self.lexer, self.formatter)

        for i in range(len(text)):
            try:
                format = self.formatter.data[position+i]
                self.setFormat(i, 1, format)
            except IndexError:
                pass


class PugdebugFormatter(Formatter):

    styles = {}

    data = []

    def __init__(self):
        super(PugdebugFormatter, self).__init__()

        for token, style in self.style:
            format = QTextCharFormat()

            if style['color']:
                color = QColor('#'+style['color'])
                format.setForeground(color)

            self.styles[token] = format

    def format(self, tokensource, outfile):
        self.data = []
        for token, value in tokensource:
            l = len(value)
            self.data.extend([self.styles[token],]*l)
