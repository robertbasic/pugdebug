# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout


class PugdebugStatusBar(QWidget):

    def __init__(self):
        super(PugdebugStatusBar, self).__init__()
        self.label = QLabel(self)

        layout = QHBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

    def set_debugging_status(self, status):
        if status == 0:
            text = "Idle ..."
        elif status == 1:
            text = 'Waiting for connection ...'
        elif status == 2:
            text = 'Debugging stopped ...'
        elif status == 3:
            text = 'Debugging in progress ...'

        self.label.setText(text)
