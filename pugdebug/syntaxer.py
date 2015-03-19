# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat

class PugdebugSyntaxer(QSyntaxHighlighter):

    phpBlock = ['<\?php', '\?>']

    keywords = ['public', 'function']

    functions = ['echo']

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

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

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

    def highlightBlock(self, text):
        for regex, nth, fmt in self.rules:
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
