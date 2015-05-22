# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QCoreApplication, QSettings
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from pugdebug.models.settings import get_projects


class PugdebugProject(QSettings):

    project_name = None
    safe_name = None

    def __init__(self, project_name):
        self.project_name = project_name
        self.safe_name = project_name.lower().replace(' ', '-')
        super(PugdebugProject, self).__init__(
            QSettings.IniFormat,
            QSettings.UserScope,
            QCoreApplication.organizationName(),
            self.safe_name
        )

        if not self.contains('project/name'):
            self.setValue('project/name', self.project_name)

    def get_project_name(self):
        return self.project_name


class PugdebugProjects(QStandardItemModel):

    def __init__(self, parent):
        super(PugdebugProjects, self).__init__(parent)

        self.setHorizontalHeaderLabels(['Name'])

        self.load_projects()

    def load_projects(self):
        for project in get_projects():
            item = QStandardItem(project)
            self.appendRow(item)
