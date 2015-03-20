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

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat

class PugdebugSyntaxer(QSyntaxHighlighter):

    rules = None
    formats = None

    def __init__(self, document, rules):
        QSyntaxHighlighter.__init__(self, document)
        self.rules = rules
        self.formats = rules.get_formats()

    def highlightBlock(self, text):
        for regex, nth, fmt in self.rules.get_rules():
            # index is the start of the highlighted part
            index = regex.indexIn(text, 0)

            while index >= 0:
                index = regex.pos(nth)
                length = len(regex.cap(nth))
                format = self.getFormat(fmt)
                self.setFormat(index, length, format)
                index = regex.indexIn(text, index+length)

    def getFormat(self, format):
        color = QColor()
        color.setRed(self.formats[format]['color'][0])
        color.setGreen(self.formats[format]['color'][1])
        color.setBlue(self.formats[format]['color'][2])
        format = QTextCharFormat()
        format.setForeground(color)

        return format

    def parse(self, string):
        pass

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
        rules += [(r'%s' % p, 0, 'phpBlock')
                for p in self.phpBlock]

        rules += [(r'%s' % k, 0, 'keywords')
                for k in self.keywords]

        rules += [(r'%s' % f, 0, 'functions')
                for f in self.functions]

        # $variables
        rules += [(r'\$[\w]*', 0, 'variables')]

        # comments
        rules += [(r'#[^\n]*', 0, 'comments')]
        rules += [(r'//[^\n]*', 0, 'comments')]
        rules += [(r'/\*+.*\*+/', 0, 'comments')]

        # strings
        rules += [(r'".*"', 0, 'strings')]
        rules += [(r"'.*'", 0, 'strings')]

        self.rules = [(QRegExp(pat), index, format)
                    for(pat, index, format) in rules]

    def get_rules(self):
        return self.rules

    def get_formats(self):
        return self.formats

    def get_syntaxer_rules_path(self):
        return "%s/pugdebug/syntaxer/" % os.getcwd()
