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
        'debugger': {
            'host': '127.0.0.1',
            'port_number': 9000,
            'idekey': 'pugdebug',
            'break_at_first_line': Qt.Checked,
            'max_depth': '3',
            'max_children': '128',
            'max_data': '512'
        },
        'path': {
            'project_root': os.path.expanduser('~'),
            'path_mapping': ''
        }
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
        """Set up initial debugger settings"""

        for group, settings in self.defaults.items():
            self.application_settings.beginGroup(group)

            for key, value in settings.items():
                if not self.application_settings.contains(key):
                    self.application_settings.setValue(key, value)

            self.application_settings.endGroup()

    def get(self, key):
        return self.application_settings.value(key)

    def has(self, key):
        return self.application_settings.contains(key)

    def set(self, key, value):
        return self.application_settings.setValue(key, value)


settings = PugdebugSettings()


def get_setting(key):
    return settings.get(key)


def has_setting(key):
    return settings.has(key)


def set_setting(key, value):
    settings.set(key, value)
