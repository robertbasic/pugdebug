# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtWidgets import QWidget, QSpinBox, QFormLayout

class PugdebugSettingsWindow(QWidget):

    layout = QFormLayout()

    def __init__(self, parent):
        super(PugdebugSettingsWindow, self).__init__(parent)

        port_number = QSpinBox()
        port_number.setRange(1, 65535)
        port_number.setValue(9000)

        layout = QFormLayout()
        self.setLayout(layout)

        layout.addRow("Port:", port_number)
