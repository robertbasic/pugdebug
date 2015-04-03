# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"


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

    def close_tab(self, tab_index):
        self.removeTab(tab_index)

        self.tabs.pop(tab_index, None)

        tabs = {}

        # Reindex the tabs
        number_of_tabs = len(self.tabs)
        if number_of_tabs > 0:
            for index in range(0, number_of_tabs):
                document_widget = self.widget(index)
                tabs[index] = document_widget.get_path()

        self.tabs = tabs

    def focus_tab(self, path):
        tab_index = self.find_tab_index_by_path(path)
        if tab_index is not None:
            self.setCurrentIndex(tab_index)

    def find_tab_index_by_path(self, path):
        tab_index = None
        for i, p in self.tabs.items():
            if p == path:
                tab_index = i
        return tab_index

    def get_current_document(self):
        index = self.currentIndex()
        return self.widget(index)

    def get_document(self, index):
        return self.widget(index)

    def get_document_by_path(self, path):
        index = self.find_tab_index_by_path(path)
        return self.widget(index)
