# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtWidgets import QPlainTextEdit
class PugdebugDocument(QPlainTextEdit):

    def __init__(self):
        super(PugdebugDocument, self).__init__()
