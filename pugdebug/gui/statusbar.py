# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout


class PugdebugStatusBar(QWidget):

    def __init__(self):
        super(PugdebugStatusBar, self).__init__()
        self.label = QLabel(self)
        self.light = QLabel(self)

        layout = QHBoxLayout()
        layout.addWidget(self.light)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def set_debugging_status(self, status):
        if status == 0:
            text = "Idle ..."
            color = "gray"
        elif status == 1:
            text = 'Waiting for connection ...'
            color = "orange"
        elif status == 2:
            text = 'Debugging stopped ...'
            color = "red"
        elif status == 3:
            text = 'Debugging in progress ...'
            color = "green"
        elif status == 4:
            text = 'Running ...'
            color = "blue"

        self.label.setText(text)

        self.pixmap = QPixmap(10, 10)
        color = QColor(color)
        self.pixmap.fill(color)
        painter = QPainter(self.pixmap)
        painter.drawRect(0, 0, 10, 10)
        self.light.setPixmap(self.pixmap)
