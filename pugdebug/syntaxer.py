# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import os
import json

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat

class PugdebugSyntaxer(QSyntaxHighlighter):

    rules = None
    formats = None

    in_php_block = 1
    in_block_comment = 2

    def __init__(self, document, rules):
        QSyntaxHighlighter.__init__(self, document)
        self.rules = rules
        self.formats = rules.get_formats()

    def highlightBlock(self, text):
        """
        If not in PHP block, only look for PHP blocks.

        If in block comment, match everything as comment

        If line has line comment, match everything from // or # as comment
        """
        # @TODO <?php $x = 'a'; ?>
        matches_ = []

        if self.previousBlockState() > 0:
            self.setCurrentBlockState(self.previousBlockState())

        if text == '':
            return

        if self.is_current_block_in_state(self.in_block_comment):
            m = {
                'start': 0,
                'end': len(text) - 1,
                'length': len(text),
                'format': 'comments'
            }
            matches_.append(m)

        """
        If not in PHP block, see if current line has one-line PHP blocks,
        get all PHP blocks from the line and get matches for them
        """
        skip_matches = False
        if not self.is_current_block_in_state(self.in_php_block):
            if text.find('<?php') < 0:
                return
            elif text.find('<?php') >= 0 and text.find('?>') >= 0:
                skip_matches = True
                matches_ = self.get_one_line_php_matches(text, matches_)

        if not skip_matches:
            matches_ = self.get_matches(text, matches_)

        if len(matches_) > 0:
            for match in matches_:
                format = self.formats[match['format']]
                self.setFormat(match['start'], match['length'], format)

    def get_one_line_php_matches(self, text, matches_):
        regex = QRegularExpression(r'.*?(<\?php(.*?)\?>)')
        php_blocks = regex.globalMatch(text)

        while php_blocks.hasNext():
            match = php_blocks.next()
            php_block = match.capturedTexts().pop(1)
            starts_at = text.find(php_block)
            matches_ = self.get_matches(php_block, matches_, starts_at)

        return matches_

    def get_matches(self, text, matches_, starts_at=0):
        for regex, format, options in self.rules.get_rules():
            if options is not None:
                regex.setPatternOptions(options)

            if self.is_current_block_in_state(self.in_block_comment) and format != 'comments':
                continue

            matches = regex.globalMatch(text)

            while matches.hasNext():
                match = matches.next()

                if match.hasMatch():
                    if match.capturedTexts().pop() == '<?php':
                        self.set_current_block(self.in_php_block)

                    if match.capturedTexts().pop() == '?>':
                        self.set_current_block(-1)

                    if match.capturedTexts().pop().startswith('/*'):
                        self.set_current_block(self.in_block_comment)

                    if match.capturedTexts().pop().endswith('*/'):
                        self.unset_current_block(self.in_block_comment)

                    m = {
                        'start': starts_at + match.capturedStart(),
                        'end': match.capturedEnd(),
                        'length': match.capturedLength(),
                        'format': format
                    }
                    matches_.append(m)

        return matches_

    def is_current_block_in_state(self, block_state):
        state = self.currentBlockState()
        if state < 0:
            return False
        has_state = (state & (1 << block_state))
        return has_state > 0

    def set_current_block(self, block_state):
        if block_state < 0:
            state = block_state
        else:
            state = self.previousBlockState()
            if state < 0:
                state = 0
            state |= 1 << block_state

        self.setCurrentBlockState(state)

    def unset_current_block(self, block_state):
        if block_state < 0:
            state = block_state
        else:
            state = self.previousBlockState()
            if state < 0:
                state = 0
            state &= ~(1 << block_state)

        self.setCurrentBlockState(state)

class PugdebugSyntaxerRules():

    keywords = []

    functions = []

    formats = {
        'phpBlock': {
            'color': (230, 0, 0)
        },
        'keywords': {
            'color': (0, 0, 230)
        },
        'functions': {
            'color': (0, 0, 230)
        },
        'variables': {
            'color': (0, 153, 0)
        },
        'dollarSign': {
            'color': (0, 255, 0)
        },
        'comments': {
            'color': (150, 150, 150)
        },
        'strings': {
            'color': (206, 123, 0)
        }
    }

    def __init__(self):
        path = self.get_syntaxer_rules_path()

        keywords_path = "%s/php_keywords.json" % path
        functions_path = "%s/php_functions.json" % path

        with open(keywords_path) as keywords_json:
            self.keywords = json.load(keywords_json)

        with open(functions_path) as functions_json:
            self.functions = json.load(functions_json)

        rules = []

        rules += [(r'<\?php', 'phpBlock', None)]

        keywords = r'\b' + r'\b|\b'.join(self.keywords) + r'\b'
        rules += [(keywords, 'keywords', None)]

        functions = r'\b' + r'\b|\b'.join(self.functions) + r'\b'
        rules += [(functions, 'functions', None)]

        # $variables
        rules += [(r'\$[\w]*', 'variables', None)]
        rules += [(r'\$(?=[\w])', 'dollarSign', None)]

        # strings
        rules += [(r'"[^"]*"', 'strings', None)]
        rules += [(r"'[^']*'", 'strings', None)]

        # comments
        rules += [(r'#[^\n]*', 'comments', None)]
        rules += [(r'//[^\n]*', 'comments', None)]
        rules += [(r'/\*+', 'comments', None)]
        rules += [(r'\*+/', 'comments', None)]

        rules += [(r'\?>', 'phpBlock', None)]

        self.rules = [(QRegularExpression(pattern), format, options)
                    for(pattern, format, options) in rules]

    def get_rules(self):
        return self.rules

    def get_formats(self):
        formats_ = {}
        for format in self.formats:
            color = QColor()
            color.setRed(self.formats[format]['color'][0])
            color.setGreen(self.formats[format]['color'][1])
            color.setBlue(self.formats[format]['color'][2])
            charFormat = QTextCharFormat()
            charFormat.setForeground(color)
            formats_[format] = charFormat
        return formats_

    def get_syntaxer_rules_path(self):
        return "%s/pugdebug/syntaxer/" % os.getcwd()
