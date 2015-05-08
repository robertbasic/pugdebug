# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import (QDialog, QLineEdit, QFormLayout,
                             QSpinBox, QCheckBox, QPushButton,
                             QVBoxLayout, QHBoxLayout)

from pugdebug.models.settings import (get_setting, set_setting,
                                      get_default_setting)


class PugdebugSettingsWindow(QDialog):

    def __init__(self, parent):
        super(PugdebugSettingsWindow, self).__init__(parent)

        self.project_root = QLineEdit()

        self.project_root.textChanged.connect(
            self.handle_project_root_changed
        )

        project_root = get_setting('path/project_root')
        self.project_root.setText(project_root)

        self.path_mapping = QLineEdit()

        self.path_mapping.textChanged.connect(
            self.handle_path_mapping_changed
        )
        path_mapping = get_setting('path/path_mapping')
        self.path_mapping.setText(path_mapping)

        self.host = QLineEdit()

        self.host.textChanged.connect(self.handle_host_changed)

        host = get_setting('debugger/host')
        self.host.setText(host)

        self.port_number = QSpinBox()
        self.port_number.setRange(1, 65535)

        self.port_number.valueChanged.connect(self.handle_port_number_changed)

        port_number = int(get_setting('debugger/port_number'))
        self.port_number.setValue(port_number)

        self.idekey = QLineEdit()

        self.idekey.textChanged.connect(self.handle_idekey_changed)

        idekey = get_setting('debugger/idekey')
        self.idekey.setText(idekey)

        self.break_at_first_line = QCheckBox("Break at first line")

        self.break_at_first_line.stateChanged.connect(
            self.handle_break_at_first_line_changed
        )

        break_at_first_line = int(get_setting('debugger/break_at_first_line'))
        self.break_at_first_line.setCheckState(break_at_first_line)

        self.max_depth = QLineEdit()

        self.max_depth.textChanged.connect(self.handle_max_depth_changed)

        max_depth = get_setting('debugger/max_depth')
        self.max_depth.setText(max_depth)

        self.max_children = QLineEdit()

        self.max_children.textChanged.connect(
            self.handle_max_children_changed
        )

        max_children = get_setting('debugger/max_children')
        self.max_children.setText(max_children)

        self.max_data = QLineEdit()

        self.max_data.textChanged.connect(self.handle_max_data_changed)

        max_data = get_setting('debugger/max_data')
        self.max_data.setText(max_data)

        # Buttons
        self.reset_button = QPushButton("Reset to defaults")
        self.reset_button.clicked.connect(self.reset_defaults)

        form_layout = QFormLayout()
        form_layout.addRow("Root:", self.project_root)
        form_layout.addRow("Maps from:", self.path_mapping)
        form_layout.addRow("Host", self.host)
        form_layout.addRow("Port", self.port_number)
        form_layout.addRow("IDE Key", self.idekey)
        form_layout.addRow("", self.break_at_first_line)
        form_layout.addRow("Max depth", self.max_depth)
        form_layout.addRow("Max children", self.max_children)
        form_layout.addRow("Max data", self.max_data)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.reset_button)

        box_layout = QVBoxLayout()
        box_layout.addLayout(form_layout)
        box_layout.addLayout(button_layout)

        self.setLayout(box_layout)

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

    def handle_max_depth_changed(self):
        value = self.max_depth.text()
        set_setting('debugger/max_depth', value)

    def handle_max_children_changed(self):
        value = self.max_children.text()
        set_setting('debugger/max_children', value)

    def handle_max_data_changed(self):
        value = self.max_data.text()
        set_setting('debugger/max_data', value)

    def reset_defaults(self):
        """Resets all settings to their deafult values"""
        self.reset_default(self.host, 'debugger/host')
        self.reset_default(self.port_number, 'debugger/port_number')
        self.reset_default(self.idekey, 'debugger/idekey')
        self.reset_default(self.break_at_first_line, 'debugger/break_at_first_line')
        self.reset_default(self.max_depth, 'debugger/max_depth')
        self.reset_default(self.max_children, 'debugger/max_children')
        self.reset_default(self.max_data, 'debugger/max_data')
        self.reset_default(self.project_root, 'path/project_root')
        self.reset_default(self.path_mapping, 'path/path_mapping')

    def reset_default(self, widget, setting):
        """Resets a single setting to its default value"""
        value = get_default_setting(setting)
        self.set_widget_value(widget, value)

    def set_widget_value(self, widget, value):
        """A generic method which can set the value of any of the used widgets.
        """
        if isinstance(widget, QLineEdit):
            widget.setText(value)
        elif isinstance(widget, QSpinBox):
            widget.setValue(value)
        elif isinstance(widget, QCheckBox):
            widget.setCheckState(value)
        else:
            name = type(widget).__name__
            raise Exception("Don't know how to set a value for %s" % name)
