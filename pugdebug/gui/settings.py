# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import (QWidget, QLineEdit, QFormLayout,
                             QSpinBox, QCheckBox)

from pugdebug.models.settings import get_setting, set_setting


class PugdebugSettingsWindow(QWidget):

    layout = QFormLayout()

    def __init__(self, parent):
        super(PugdebugSettingsWindow, self).__init__(parent)

        self.project_root = QLineEdit()

        self.project_root.editingFinished.connect(
            self.handle_project_root_changed
        )

        project_root = get_setting('path/project_root')
        self.project_root.setText(project_root)

        self.path_mapping = QLineEdit()

        self.path_mapping.editingFinished.connect(
            self.handle_path_mapping_changed
        )
        path_mapping = get_setting('path/path_mapping')
        self.path_mapping.setText(path_mapping)

        self.host = QLineEdit()

        self.host.editingFinished.connect(self.handle_host_changed)

        host = get_setting('debugger/host')
        self.host.setText(host)

        self.port_number = QSpinBox()
        self.port_number.setRange(1, 65535)

        self.port_number.valueChanged.connect(self.handle_port_number_changed)

        port_number = int(get_setting('debugger/port_number'))
        self.port_number.setValue(port_number)

        self.idekey = QLineEdit()

        self.idekey.editingFinished.connect(self.handle_idekey_changed)

        idekey = get_setting('debugger/idekey')
        self.idekey.setText(idekey)

        self.break_at_first_line = QCheckBox("Break at first line")

        self.break_at_first_line.stateChanged.connect(
            self.handle_break_at_first_line_changed
        )

        break_at_first_line = int(get_setting('debugger/break_at_first_line'))
        print(break_at_first_line)
        self.break_at_first_line.setCheckState(break_at_first_line)

        layout = QFormLayout()
        self.setLayout(layout)

        layout.addRow("Root:", self.project_root)
        layout.addRow("Maps from:", self.path_mapping)
        layout.addRow("Host", self.host)
        layout.addRow("Port", self.port_number)
        layout.addRow("IDE Key", self.idekey)
        layout.addRow("", self.break_at_first_line)

    def get_project_root(self):
        return self.project_root.text()

    def get_path_mapping(self):
        path_map = self.path_mapping.text()

        if len(path_map) > 0:
            return path_map

        return False

    def handle_project_root_changed(self):
        value = self.project_root.text()
        set_setting('path/project_root', value)

    def handle_path_mapping_changed(self):
        value = self.path_mapping.text()
        set_setting('path/path_mapping', value)

    def handle_host_changed(self):
        value = self.host.text()
        set_setting('debugger/host', value)

    def handle_port_number_changed(self, value):
        """Handle when port number gets changed

        Set the new value in the application's setting.
        """
        set_setting('debugger/port_number', value)

    def handle_idekey_changed(self):
        value = self.idekey.text()
        set_setting('debugger/idekey', value)

    def handle_break_at_first_line_changed(self, value):
        set_setting('debugger/break_at_first_line', value)
