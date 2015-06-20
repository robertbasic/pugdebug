# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import os

from PyQt5.QtCore import QCoreApplication, QSettings
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from pugdebug.models.settings import (get_projects, delete_project,
                                      get_setting, has_setting,
                                      remove_setting)


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

    def is_project_current(self):
        if has_setting('current_project'):
            current_project = get_setting('current_project')

            if current_project == self.get_project_name():
                return True

        return False

    def get_settings(self):
        project_settings = {}

        for key in self.allKeys():
            if has_setting(key):
                project_settings[key] = self.value(key)

        return project_settings

    def set_settings(self, new_settings):
        for key, value in new_settings.items():
            self.setValue(key, value)

    def delete(self):
        if self.is_project_current():
            remove_setting('current_project')

        delete_project(self.get_project_name())

        filename = self.fileName()
        try:
            os.unlink(filename)
        except OSError as e:
            print(e)


class PugdebugProjects(QStandardItemModel):

    def __init__(self, parent):
        super(PugdebugProjects, self).__init__(parent)

        self.load_projects()

    def load_projects(self):
        self.clear()

        self.setHorizontalHeaderLabels(['Name'])

        for project in get_projects():
            item = QStandardItem(project)
            item.setEditable(False)
            self.appendRow(item)

        self.sort(0)

    def get_project_by_index(self, index):
        item = self.itemFromIndex(index)
        return self.get_project_by_item(item)

    def get_project_by_item(self, item):
        project_name = item.text()
        return PugdebugProject(project_name)
