# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QCoreApplication, QSettings


class PugdebugSettings():

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

        self.setup_debugger_settings()

    def setup_debugger_settings(self):
        """Set up initial debugger settings

        Sets up the initial port number to 9000.
        """
        self.application_settings.beginGroup("debugger")

        if not self.application_settings.contains('port_number'):
            self.application_settings.setValue('port_number', 9000)

        self.application_settings.endGroup()

    def get(self, key):
        return self.application_settings.value(key)

    def set(self, key, value):
        return self.application_settings.setValue(key, value)


settings = PugdebugSettings()


def get_setting(key):
    return settings.get(key)


def set_setting(key, value):
    settings.set(key, value)
