# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import sys
import unittest

from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView
from pugdebug.pugdebug import Pugdebug

class PugdebugTest(unittest.TestCase):

    def setUp(self):
        self.app = QApplication(sys.argv)
        self.pugdebug = Pugdebug()

    def test_main_window_setup_correctly(self):
        self.assertIsInstance(self.pugdebug.main_window, QMainWindow)
        self.assertIsInstance(self.pugdebug.file_browser, QTreeView)
