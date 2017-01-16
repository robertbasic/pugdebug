# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from pygments import highlight, formatter
from pygments.lexers.php import PhpLexer

from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat


class PugdebugSyntaxer(QSyntaxHighlighter):

    formatter = None
    lexer = None

    token_multilines = {
        1: 'Token.Literal.String.Doc',
        2: 'Token.Comment.Multiline',
        3: 'Token.Literal.String.Single',
        4: 'Token.Literal.String.Double',
        5: 'Token.Literal.String'
    }

    def __init__(self, document, formatter):
        super(PugdebugSyntaxer, self).__init__(document)

        self.formatter = formatter
        self.lexer = PhpLexer()

        self.highlight()

    def highlight(self):
        document = self.document()
        self.formatter.document = document
        highlight(document.toPlainText(), self.lexer, self.formatter)

    def highlightBlock(self, text):
        block = self.currentBlock()
        block_number = block.blockNumber()

        # Formats for the current block
        block_formats = None

        if block_number in self.formatter.formats:
            block_formats = self.formatter.formats[block_number]

        # If the current block has no formats
        # see if the previous was maybe a block format
        # like a multiline comment or a docblock
        # and use that format
        if block_formats is None:
            previous_block_state = self.previousBlockState()
            if previous_block_state > 0:
                block_formats = self.__get_multiline_format(
                    text,
                    previous_block_state
                )
                self.formatter.formats[block_number] = block_formats

        if block_formats is not None:
            for block_format in block_formats:

                # Mark the current block state if needed
                if block_format['token'] == 'Token.Literal.String.Doc':
                    self.setCurrentBlockState(1)
                elif block_format['token'] == 'Token.Comment.Multiline':
                    self.setCurrentBlockState(2)
                elif block_format['token'] == 'Token.Literal.String.Single':
                    self.setCurrentBlockState(3)
                elif block_format['token'] == 'Token.Literal.String.Double':
                    self.setCurrentBlockState(4)
                elif block_format['token'] == 'Token.Literal.String':
                    self.setCurrentBlockState(5)

                # The end of multiline comments/docblocks is a weird Token.Text
                # so if current token is Token.Text
                # and the previous state was a multiline state
                # highlight the current block as a multiline
                previous_block_state = self.previousBlockState()

                if block_format['token'] == 'Token.Text':
                    if previous_block_state > 0:
                        block_format = self.__get_multiline_format(
                            text, previous_block_state
                        ).pop()

                if block_format['token'] == 'Token.Punctuation':
                    self.setCurrentBlockState(-1)

                start = block_format['start']
                end = block_format['end']
                style = block_format['style']
                self.setFormat(start, end, style)

    def __get_multiline_format(self, text, token_index):
        token = self.token_multilines[token_index]
        return [{
            'start': 0,
            'end': len(text),
            'style': self.formatter.styles[token],
            'token': token
        }]


class PugdebugFormatter(formatter.Formatter):

    styles = {}

    formats = {}

    document = None

    def __init__(self):
        super(PugdebugFormatter, self).__init__()

        for token, style in self.style:
            format = QTextCharFormat()

            if style['color']:
                color = QColor('#' + style['color'])
                format.setForeground(color)

            self.styles[str(token)] = format

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
            token = str(token)
            # Find the block which has the current value, by it's position
            block = self.document.findBlock(current_value_position)
            block_number = block.blockNumber()

            # If we advanced a block
            if current_block_number < block_number:
                block_text = block.text()

                # When there are 2 or more indented one line comments
                # Except for the 1st line, pygments sees the indents as tokens
                # so if the current value stripped of whitespace from the left
                # is an empty string, skip it
                if value.lstrip() != '':
                    # Where do we start in the current block,
                    # whitespace included?
                    start_in_block = len(block_text) - len(block_text.lstrip())

                    current_block_number = block_number

            # If this block has no formats yet
            if block_number not in self.formats:
                self.formats[block_number] = []

            length = len(value)
            end = start_in_block + length
            style = self.styles[token]

            # Format for the current value
            format = {
                'start': start_in_block,
                'end': end,
                'style': style,
                'token': token
            }

            start_in_block += length
            current_value_position += length

            self.formats[block_number].append(format)
