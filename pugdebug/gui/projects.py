# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QDialog, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QTreeView, QAction, QMenu,
                             QMessageBox)
from PyQt5.QtGui import QIcon, QFont

from pugdebug.gui.forms import PugdebugSettingsForm
from pugdebug.models.projects import PugdebugProject
from pugdebug.models.settings import get_default_setting, add_project


class PugdebugNewProjectWindow(QDialog):

    def __init__(self, parent):
        super(PugdebugNewProjectWindow, self).__init__(parent)

        self.parent = parent

        self.setWindowTitle("New project")

        self.form = PugdebugSettingsForm()

        self.project_name = QLineEdit()

        self.accepted.connect(self.create_new_project)

        self.setup_layout()
        self.setup_fonts()

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
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        box_layout = QVBoxLayout()
        box_layout.addLayout(project_name_layout)
        box_layout.addWidget(self.form.path_group)
        box_layout.addWidget(self.form.debugger_group)
        box_layout.addLayout(button_layout)

        self.setLayout(box_layout)

    def setup_fonts(self):
        font = QFont('mono')
        font.setStyleHint(QFont.Monospace)
        font.setPixelSize(12)
        self.setFont(font)

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

    project_deleted_signal = pyqtSignal(bool)

    def __init__(self):
        super(PugdebugProjectsBrowser, self).__init__()

        self.delete_action = QAction(
            QIcon.fromTheme('list-remove'),
            "&Delete",
            self
        )
        self.delete_action.triggered.connect(self.handle_delete_action)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def load_projects(self):
        model = self.model()
        model.load_projects()

    def load_project_by_name(self, project_name):
        model = self.model()
        items = model.findItems(project_name)
        if len(items) > 0:
            item = items[0]
            project = model.get_project_by_item(item)
            return project

        return None

    def show_context_menu(self, point):
        context_menu = QMenu(self)

        if self.indexAt(point):
            context_menu.addAction(self.delete_action)

        point = self.mapToGlobal(point)
        context_menu.popup(point)

    def handle_delete_action(self):
        index = self.selectedIndexes().pop()

        project = self.model().get_project_by_index(index)

        messageBox = QMessageBox()
        text = "Deleting the %s project" % project.get_project_name()
        messageBox.setText(text)
        messageBox.setInformativeText("Are you sure you want to delete this"
                                      " project?")

        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        answer = messageBox.exec()

        if answer == QMessageBox.Yes:
            is_project_current = project.is_project_current()

            project.delete()

            self.load_projects()

            self.project_deleted_signal.emit(is_project_current)
