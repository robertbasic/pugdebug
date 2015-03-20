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
        matches_ = []

        if self.previousBlockState() > 0:
            self.setCurrentBlockState(self.previousBlockState())

        rules = self.rules.get_rules()

        if not self.is_current_block_in_state(self.in_php_block):
            rules = self.rules.get_php_rules()

        for pattern, format, options in rules:
            regex = QRegularExpression(pattern)
            if options is not None:
                regex.setPatternOptions(options)

            if self.is_current_block_in_state(self.in_block_comment) and format != 'comments':
                m = {
                    'start': 0,
                    'end': len(text) - 1,
                    'length': len(text),
                    'format': 'comments'
                }
                matches_.append(m)
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
                        'start': match.capturedStart(),
                        'end': match.capturedEnd(),
                        'length': match.capturedLength(),
                        'format': format
                    }
                    matches_.append(m)

        if len(matches_) > 0:
            for match in matches_:
                format = self.getFormat(match['format'])
                self.setFormat(match['start'], match['length'], format)

    def getFormat(self, format):
        color = QColor()
        color.setRed(self.formats[format]['color'][0])
        color.setGreen(self.formats[format]['color'][1])
        color.setBlue(self.formats[format]['color'][2])
        format = QTextCharFormat()
        format.setForeground(color)

        return format

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

    phpBlock = ['<\?php', '\?>']

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

        rules += self.get_php_rules()

        # comments
        rules += [(r'#[^\n]*', 'comments', None)]
        rules += [(r'//[^\n]*', 'comments', None)]
        rules += [(r'/\*+', 'comments', None)]
        rules += [(r'\*+/', 'comments', None)]

        # $variables
        rules += [(r'\$[\w]*', 'variables', None)]

        rules += [(r'\b%s\b' % k,'keywords', None) for k in self.keywords]

        rules += [(r'\b%s\b' % f, 'functions', None) for f in self.functions]


        # strings
        rules += [(r'"[^"]*"', 'strings', None)]
        rules += [(r"'[^']*'", 'strings', None)]

        self.rules = [(pattern, format, options)
                    for(pattern, format, options) in rules]

    def get_php_rules(self):
        return [(r'%s' % p, 'phpBlock', None)
                for p in self.phpBlock]

    def get_rules(self):
        return self.rules

    def get_formats(self):
        return self.formats

    def get_syntaxer_rules_path(self):
        return "%s/pugdebug/syntaxer/" % os.getcwd()
