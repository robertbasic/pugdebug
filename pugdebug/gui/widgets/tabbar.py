# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "ihabunek"

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTabBar


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

        If it's the middle button, remember which over which tab it was pressed.
        """
        if mouseEvent.button() == Qt.MidButton:
            self.previousIndex = self.tabAt(mouseEvent.pos())
        QTabBar.mousePressEvent(self, mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """Triggered when a mouse button is released.

        If a middle button was pressed previously, and if it is released over
        the same tab, emit the signal.
        """
        if mouseEvent.button() == Qt.MidButton and \
            self.previousIndex == self.tabAt(mouseEvent.pos()):
            self.middle_clicked_signal.emit(self.previousIndex)
        self.previousIndex = -1
        QTabBar.mouseReleaseEvent(self, mouseEvent)
