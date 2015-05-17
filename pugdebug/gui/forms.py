# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import (QLineEdit, QFormLayout, QSpinBox, QCheckBox,
                             QGroupBox)


class PugdebugSettingsForm():

    def __init__(self):
        # Construct the widgets
        self.widgets = {
            'path/project_root': QLineEdit(),
            'path/path_mapping': QLineEdit(),
            'debugger/host': QLineEdit(),
            'debugger/port_number': QSpinBox(),
            'debugger/idekey': QLineEdit(),
            'debugger/break_at_first_line': QCheckBox("Break at first line"),
            'debugger/max_depth': QLineEdit(),
            'debugger/max_children': QLineEdit(),
            'debugger/max_data': QLineEdit(),
        }

        # Widget settings
        self.widgets['debugger/port_number'].setRange(1, 65535)

        self.setup_path_widgets()
        self.setup_debugger_widgets()

    def setup_path_widgets(self):
        path_layout = QFormLayout()
        path_layout.addRow("Root:", self.widgets['path/project_root'])
        path_layout.addRow("Maps from:", self.widgets['path/path_mapping'])

        self.path_group = QGroupBox("Path")
        self.path_group.setLayout(path_layout)

    def setup_debugger_widgets(self):
        debugger_layout = QFormLayout()
        debugger_layout.addRow("Host", self.widgets['debugger/host'])
        debugger_layout.addRow("Port", self.widgets['debugger/port_number'])
        debugger_layout.addRow("IDE Key", self.widgets['debugger/idekey'])
        debugger_layout.addRow(
            "",
            self.widgets['debugger/break_at_first_line']
        )
        debugger_layout.addRow("Max depth", self.widgets['debugger/max_depth'])
        debugger_layout.addRow(
            "Max children",
            self.widgets['debugger/max_children']
        )
        debugger_layout.addRow("Max data", self.widgets['debugger/max_data'])

        self.debugger_group = QGroupBox("Debugger")
        self.debugger_group.setLayout(debugger_layout)
