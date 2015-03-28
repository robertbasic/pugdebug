# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import os

from PyQt5.QtWidgets import QWidget, QLineEdit, QFormLayout

class PugdebugSettingsWindow(QWidget):

    layout = QFormLayout()

    def __init__(self, parent):
        super(PugdebugSettingsWindow, self).__init__(parent)

        home_path = os.path.expanduser('~')

        self.project_root = QLineEdit(home_path)
        self.project_root.setMaximumWidth(250)

        self.path_mapping = QLineEdit()
        self.path_mapping.setMaximumWidth(250)

        layout = QFormLayout()
        self.setLayout(layout)

        layout.addRow("Root:", self.project_root)
        layout.addRow("Maps from:", self.path_mapping)

    def get_project_root(self):
        return self.project_root.text()

    def get_path_mapping(self):
        path_map = self.path_mapping.text()

        if len(path_map) > 0:
            return path_map

        return False
