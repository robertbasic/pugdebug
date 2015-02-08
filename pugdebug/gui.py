# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    All GUI elements for pugdebug.

    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QMainWindow

from pugdebug.elements import PugdebugFileBrowser

class PugdebugMainWindow(QMainWindow):

    def __init__(self):
        super(PugdebugMainWindow, self).__init__()
        self.setObjectName("pugdebug")
        self.setWindowTitle("pugdebug")

        self.setup_docks()

        self.setup_file_browser()

    def setup_docks(self):
        self.files_dock = QDockWidget("Files", self)
        self.files_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.files_dock)

    def setup_file_browser(self):
        self.file_browser = PugdebugFileBrowser()

        self.files_dock.setWidget(self.file_browser)
