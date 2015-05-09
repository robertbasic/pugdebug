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
                             QVBoxLayout, QHBoxLayout, QGroupBox)

from PyQt5.QtCore import pyqtSignal

from pugdebug.models.settings import (get_setting, has_setting, set_setting,
                                      get_default_setting)


class PugdebugSettingsWindow(QDialog):

    settings_changed_signal = pyqtSignal(set)

    def __init__(self, parent):
        super(PugdebugSettingsWindow, self).__init__(parent)

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

        # Save values on accepted (clicked Save button)
        self.accepted.connect(self.save_settings)

        self.setup_layout()

    def setup_layout(self):
        # Buttons
        reset_button = QPushButton("&Reset")
        reset_button.clicked.connect(self.reset_defaults)

        save_button = QPushButton("&Save")
        save_button.clicked.connect(self.accept)

        cancel_button = QPushButton("&Cancel")
        cancel_button.clicked.connect(self.reject)

        # Layout
        path_layout = QFormLayout()
        path_layout.addRow("Root:", self.widgets['path/project_root'])
        path_layout.addRow("Maps from:", self.widgets['path/path_mapping'])

        debugger_layout = QFormLayout()
        debugger_layout.addRow("Host", self.widgets['debugger/host'])
        debugger_layout.addRow("Port", self.widgets['debugger/port_number'])
        debugger_layout.addRow("IDE Key", self.widgets['debugger/idekey'])
        debugger_layout.addRow("", self.widgets['debugger/break_at_first_line'])
        debugger_layout.addRow("Max depth", self.widgets['debugger/max_depth'])
        debugger_layout.addRow("Max children", self.widgets['debugger/max_children'])
        debugger_layout.addRow("Max data", self.widgets['debugger/max_data'])

        path_group = QGroupBox("Path")
        path_group.setLayout(path_layout)

        debugger_group = QGroupBox("Debugger")
        debugger_group.setLayout(debugger_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(reset_button)

        box_layout = QVBoxLayout()
        box_layout.addWidget(path_group)
        box_layout.addWidget(debugger_group)
        box_layout.addLayout(button_layout)

        self.setLayout(box_layout)

    def showEvent(self, event):
        """Load setting from store when showing the dialog."""
        super(PugdebugSettingsWindow, self).showEvent(event)
        self.load_settings()

    def get_project_root(self):
        widget = self.widgets['path/project_root']
        return self.get_widget_value(widget)

    def get_path_mapping(self):
        widget = self.widgets['path/path_mapping']
        path_map = self.get_widget_value(widget)

        if len(path_map) > 0:
            return path_map

        return False

    def load_settings(self):
        """Loads all settings from QSettings into the form"""
        for name, widget in self.widgets.items():
            value = get_setting(name) if has_setting(name) \
                else get_default_setting(name)
            self.set_widget_value(widget, value)

    def save_settings(self):
        """Saves all settings from the form to QSettings"""
        changed_settings = set()

        for name, widget in self.widgets.items():
            value = self.get_widget_value(widget)

            if not has_setting(name) or get_setting(name) != value:
                set_setting(name, value)
                changed_settings.add(name)

        if len(changed_settings) > 0:
            self.settings_changed_signal.emit(changed_settings)

    def reset_defaults(self):
        """Resets all settings to their deafult values"""
        for name, widget in self.widgets.items():
            value = get_default_setting(name)
            self.set_widget_value(widget, value)

    def set_widget_value(self, widget, value):
        """A generic method which can set the value of any of the used widgets.
        """
        if isinstance(widget, QLineEdit):
            widget.setText(value)
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value))
        elif isinstance(widget, QCheckBox):
            widget.setCheckState(value)
        else:
            name = type(widget).__name__
            raise Exception("Don't know how to set a value for %s" % name)

    def get_widget_value(self, widget):
        """A generic method which can set the value of any of the used widgets.
        """
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QCheckBox):
            return widget.checkState()
        else:
            name = type(widget).__name__
            raise Exception("Don't know how to get a value for %s" % name)
