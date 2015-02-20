# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import sys

from pugdebug.debugger import PugdebugDebugger
from pugdebug.gui.main_window import PugdebugMainWindow
from pugdebug.gui.document import PugdebugDocument
from pugdebug.models.documents import PugdebugDocuments
from pugdebug.models.file_browser import PugdebugFileBrowser

class Pugdebug():

    def __init__(self):
        self.debugger = PugdebugDebugger()

        self.main_window = PugdebugMainWindow()
        self.file_browser = self.main_window.get_file_browser()
        self.document_viewer = self.main_window.get_document_viewer()

        self.documents = PugdebugDocuments()

        self.setup_file_browser()

        self.connect_signals()

    def setup_file_browser(self):
        model = PugdebugFileBrowser(self.main_window)
        self.file_browser.setModel(model)
        self.file_browser.setRootIndex(model.start_index)
        self.file_browser.hide_columns()

    def connect_signals(self):
        self.connect_file_browser_signals()

        self.connect_toolbar_action_signals()

    def connect_file_browser_signals(self):
        self.file_browser.activated.connect(self.file_browser_item_activated)

    def connect_toolbar_action_signals(self):
        self.main_window.start_debug_action.triggered.connect(self.start_debug)
        self.main_window.stop_debug_action.triggered.connect(self.stop_debug)
        self.main_window.step_over_action.triggered.connect(self.step_over)
        self.main_window.step_into_action.triggered.connect(self.step_into)
        self.main_window.step_out_action.triggered.connect(self.step_out)

    def file_browser_item_activated(self, index):
        path = self.file_browser.model().filePath(index)
        self.open_document(path)

    def open_document(self, path):
        if not self.documents.is_document_open(path):
            document = self.documents.open_document(path)

            doc = PugdebugDocument()
            doc.appendPlainText(document.contents)

            self.document_viewer.add_tab(doc, document.filename, path)
        else:
            self.document_viewer.focus_tab(path)

    def start_debug(self):
        self.debugger.start_debug()

        index_file = self.debugger.get_index_file()
        self.open_document(index_file)

        self.step_into()

    def stop_debug(self):
        self.debugger.stop_debug()

    def step_over(self):
        self.debugger.step_over()

    def step_into(self):
        self.debugger.step_into()

        self.focus_current_line()

    def step_out(self):
        self.debugger.step_out()

    def run(self):
        self.main_window.showMaximized()
