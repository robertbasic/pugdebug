# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QDialog, QLineEdit, QSpinBox, QCheckBox,
                             QPushButton, QVBoxLayout, QHBoxLayout)

from pugdebug.gui.forms import PugdebugSettingsForm
from pugdebug.models.settings import (get_setting, has_setting, set_setting,
                                      get_default_setting)


class PugdebugSettingsWindow(QDialog):

    settings_changed_signal = pyqtSignal(set)

    def __init__(self, parent):
        super(PugdebugSettingsWindow, self).__init__(parent)

        self.form = PugdebugSettingsForm()

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

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(reset_button)

        box_layout = QVBoxLayout()
        box_layout.addWidget(self.form.path_group)
        box_layout.addWidget(self.form.debugger_group)
        box_layout.addLayout(button_layout)

        self.setLayout(box_layout)

    def showEvent(self, event):
        """Load setting from store when showing the dialog."""
        super(PugdebugSettingsWindow, self).showEvent(event)
        self.load_settings()

    def get_project_root(self):
        widget = self.form.widgets['path/project_root']
        return self.form.get_widget_value(widget)

    def get_path_mapping(self):
        widget = self.form.widgets['path/path_mapping']
        path_map = self.form.get_widget_value(widget)

        if len(path_map) > 0:
            return path_map

        return False

    def load_settings(self):
        """Loads all settings from QSettings into the form"""
        for name, widget in self.form.widgets.items():
            value = get_setting(name) if has_setting(name) \
                else get_default_setting(name)
            self.form.set_widget_value(widget, value)

    def save_settings(self):
        """Saves all settings from the form to QSettings"""
        changed_settings = set()

        for name, widget in self.form.widgets.items():
            value = self.form.get_widget_value(widget)

            if not has_setting(name) or get_setting(name) != value:
                set_setting(name, value)
                changed_settings.add(name)

        if len(changed_settings) > 0:
            self.settings_changed_signal.emit(changed_settings)

    def reset_defaults(self):
        """Resets all settings to their deafult values"""
        for name, widget in self.form.widgets.items():
            value = get_default_setting(name)
            self.form.set_widget_value(widget, value)
