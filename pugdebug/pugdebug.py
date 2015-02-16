# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import sys

from PyQt5.QtWidgets import QApplication
from pugdebug.gui.main_window import PugdebugMainWindow

class Pugdebug(QApplication):

    def __init__(self, argv):
        super(Pugdebug, self).__init__(argv)

        self.main_window = PugdebugMainWindow()
        self.file_browser = self.main_window.get_file_browser()

        self.connect_signals()

    def connect_signals(self):
        self.connect_file_browser()

    def connect_file_browser(self):
        self.file_browser.activated.connect(self.file_browser_item_activated)

    def file_browser_item_activated(self, index):
        print(self.file_browser.model().filePath(index))

    def run(self):
        self.main_window.showMaximized()
        sys.exit(self.exec_())
