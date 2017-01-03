# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QTabBar


class PugdebugDocumentViewer(QTabWidget):

    tabs = {}

    def __init__(self):
        super(PugdebugDocumentViewer, self).__init__()

        # Use the extended tab bar wiget to have middle click close tabs
        self.tab_bar = PugdebugTabBar()
        self.tab_bar.middle_clicked_signal.connect(self.close_tab)
        self.setTabBar(self.tab_bar)

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

    def get_all_documents(self):
        documents = []
        for i, p in self.tabs.items():
            documents.append(self.widget(i))
        return documents

    def remove_line_highlights(self):
        for index, path in self.tabs.items():
            self.widget(index).remove_line_highlights()


class PugdebugTabBar(QTabBar):
    """Adds a signal when the middle button is clicked to the QTabBar widget.

    A click is defined as a press event followed by a release event over the
    same tab.

    Stolen from: http://stackoverflow.com/a/9445581/84245
    """
    middle_clicked_signal = pyqtSignal(int)

    def __init__(self):
        super(QTabBar, self).__init__()
        self.previousMiddleIndex = -1

    def mousePressEvent(self, mouseEvent):
        """Triggered when a mouse button is pressed.

        If it's the middle button, remember which over which tab it
        was pressed.
        """
        if mouseEvent.button() == Qt.MidButton:
            self.previousIndex = self.tabAt(mouseEvent.pos())
        QTabBar.mousePressEvent(self, mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """Triggered when a mouse button is released.

        If a middle button was pressed previously, and if it is released over
        the same tab, emit the signal.
        """
        if (mouseEvent.button() == Qt.MidButton and
                self.previousIndex == self.tabAt(mouseEvent.pos())):
            self.middle_clicked_signal.emit(self.previousIndex)
        self.previousIndex = -1
        QTabBar.mouseReleaseEvent(self, mouseEvent)
