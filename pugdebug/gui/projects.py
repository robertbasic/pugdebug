# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import (QDialog, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QTreeView)

from pugdebug.gui.forms import PugdebugSettingsForm
from pugdebug.models.projects import PugdebugProject
from pugdebug.models.settings import get_default_setting, add_project


class PugdebugNewProjectWindow(QDialog):

    def __init__(self, parent):
        super(PugdebugNewProjectWindow, self).__init__(parent)

        self.parent = parent

        self.form = PugdebugSettingsForm()

        self.project_name = QLineEdit()

        self.accepted.connect(self.create_new_project)

        self.setup_layout()

        self.load_settings()

    def setup_layout(self):
        project_name_layout = QFormLayout()
        project_name_layout.addRow("Project name:", self.project_name)

        # Buttons
        save_button = QPushButton("&Save")
        save_button.clicked.connect(self.accept)

        cancel_button = QPushButton("&Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        box_layout = QVBoxLayout()
        box_layout.addLayout(project_name_layout)
        box_layout.addWidget(self.form.path_group)
        box_layout.addWidget(self.form.debugger_group)
        box_layout.addLayout(button_layout)

        self.setLayout(box_layout)

    def create_new_project(self):
        project_name = self.project_name.text()
        project = PugdebugProject(project_name)

        for name, widget in self.form.widgets.items():
            value = self.form.get_widget_value(widget)
            project.setValue(name, value)

        project_name = project.get_project_name()

        add_project(project_name)

        self.parent.new_project_created_signal.emit(project_name)

    def load_settings(self):
        """Load default settings into the form"""
        for name, widget in self.form.widgets.items():
            value = get_default_setting(name)
            self.form.set_widget_value(widget, value)


class PugdebugProjectsBrowser(QTreeView):

    def __init__(self):
        super(PugdebugProjectsBrowser, self).__init__()

    def load_projects(self):
        model = self.model()
        model.load_projects()
