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

    buffer = 0

    def __init__(self, document, formatter):
        super(PugdebugSyntaxer, self).__init__(document)

        self.formatter = formatter
        self.lexer = PhpLexer()

        self.formatter.document = document

        highlight(self.document().toPlainText(), self.lexer, self.formatter)

    def highlightBlock(self, text):
        block = self.currentBlock()
        block_number = block.blockNumber()

        block_format = None

        if block_number in self.formatter.formats:
            block_format = self.formatter.formats[block_number]

        if block_format is not None:
            for format in block_format:
                self.setFormat(format['start'], format['end'], format['style'])

class PugdebugFormatter(Formatter):

    styles = {}

    formats = {}

    document = None

    def __init__(self):
        super(PugdebugFormatter, self).__init__()

        for token, style in self.style:
            format = QTextCharFormat()

            if style['color']:
                color = QColor('#'+style['color'])
                format.setForeground(color)

            self.styles[token] = format

    def format(self, tokensource, outfile):
        """Format source file

        Formats are separated block by block.
        """
        # Formats for every block, block by block
        self.formats = {}
        # Position of value in the source
        current_value_position = 0
        # The number of the current block
        current_block_number = -1
        # Where does text start in the current block
        # Used to skip whitespace on the beginning of line
        start_in_block = 0
        # The text of the current block
        block_text = ''

        for token, value in tokensource:
            # Find the block which has the current value, by it's position
            block = self.document.findBlock(current_value_position)
            block_number = block.blockNumber()

            # If we advanced a block
            if current_block_number < block_number:
                block_text = block.text()
                # Where do we start in the current block, whitespace included?
                start_in_block = len(block_text) - len(block_text.lstrip())
                current_block_number = block_number

            # If this block has no formats yet
            if block_number not in self.formats:
                self.formats[block_number] = []

            length = len(value)
            end = start_in_block + length
            # Format for the current value
            format = {
                'start': start_in_block,
                'end': end,
                'style': self.styles[token]
            }
            start_in_block += length
            current_value_position += length

            self.formats[block_number].append(format)
