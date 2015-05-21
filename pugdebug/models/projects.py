# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QCoreApplication, QSettings


class PugdebugProject(QSettings):

    def __init__(self, project_name):
        project_name = project_name.lower().replace(' ', '-')
        super(PugdebugProject, self).__init__(
            QSettings.IniFormat,
            QSettings.UserScope,
            QCoreApplication.organizationName(),
            project_name
        )
        self.setValue('project', project_name)
