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
from pugdebug.gui.document import PugdebugDocument
from pugdebug.models.documents import PugdebugDocuments

class Pugdebug(QApplication):

    def __init__(self, argv):
        super(Pugdebug, self).__init__(argv)

        self.main_window = PugdebugMainWindow()
        self.file_browser = self.main_window.get_file_browser()
        self.document_viewer = self.main_window.get_document_viewer()

        self.documents = PugdebugDocuments()

        self.connect_signals()

    def connect_signals(self):
        self.connect_file_browser_signals()

    def connect_file_browser_signals(self):
        self.file_browser.activated.connect(self.file_browser_item_activated)

    def file_browser_item_activated(self, index):
        path = self.file_browser.model().filePath(index)
        self.open_document(path)

    def open_document(self, path):
        document = self.documents.open_document(path)

        doc = PugdebugDocument()
        doc.appendPlainText(document.contents)

        tab_index = self.document_viewer.addTab(doc, document.filename)
        self.document_viewer.setCurrentIndex(tab_index)

    def run(self):
        self.main_window.showMaximized()
        sys.exit(self.exec_())
