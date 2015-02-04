# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    All GUI elements for pugdebug.

    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

class PugdebugMain():

    def __init__(self, parent):
        self.parent = parent

        self.parent.setObjectName("pugdebug")
        self.parent.setWindowTitle("pugdebug")
