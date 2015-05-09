# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import os

from PyQt5.QtCore import QCoreApplication, QSettings, Qt


class PugdebugSettings():

    defaults = {
        'debugger/host': '127.0.0.1',
        'debugger/port_number': 9000,
        'debugger/idekey': 'pugdebug',
        'debugger/break_at_first_line': Qt.Checked,
        'debugger/max_depth': '3',
        'debugger/max_children': '128',
        'debugger/max_data': '512',

        'path/project_root': os.path.expanduser('~'),
        'path/path_mapping': ''
    }

    def __init__(self):
        """Model object to handle application settings

        Sets up initial application settings.

        QSettings promises to work cross-platform.
        """
        QCoreApplication.setOrganizationName("pugdebug")
        QCoreApplication.setOrganizationDomain(
            "http://github.com/robertbasic/pugdebug"
        )
        QCoreApplication.setApplicationName("pugdebug")
        self.application_settings = QSettings()

        self.setup_default_settings()

    def setup_default_settings(self):
        """Set the default values for settings which don't have a value."""
        for key, value in self.defaults.items():
            if not self.has(key):
                self.set(key, value)

    def get(self, key):
        return self.application_settings.value(key)

    def get_default(self, key):
        return self.defaults[key] if key in self.defaults else None

    def has(self, key):
        return self.application_settings.contains(key)

    def set(self, key, value):
        return self.application_settings.setValue(key, value)


settings = PugdebugSettings()


def get_setting(key):
    return settings.get(key)


def get_default_setting(key):
    return settings.get_default(key)


def has_setting(key):
    return settings.has(key)


def set_setting(key, value):
    settings.set(key, value)
