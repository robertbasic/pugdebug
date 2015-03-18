# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtWidgets import QTabWidget

class PugdebugDocumentViewer(QTabWidget):

    tabs = {}

    def __init__(self):
        super(PugdebugDocumentViewer, self).__init__()

        self.setTabsClosable(True)

    def add_tab(self, document_widget, filename, path):
        tab_index = self.addTab(document_widget, filename)
        self.setCurrentIndex(tab_index)

        self.tabs[tab_index] = path

    def focus_tab(self, path):
        tab_index = None
        for i, p in self.tabs.items():
            if p == path:
                tab_index = i

        if tab_index is not None:
            self.setCurrentIndex(tab_index)

    def get_current_document(self):
        index = self.currentIndex()
        return self.widget(index)
