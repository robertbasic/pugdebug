# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    All GUI elements for pugdebug.

    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from pugdebug.models import PugdebugFileBrowser
from pugdebug.viewers import *

class PugdebugMainWindow(QMainWindow):

    def __init__(self):
        super(PugdebugMainWindow, self).__init__()
        self.setObjectName("pugdebug")
        self.setWindowTitle("pugdebug")

        self.central_widget_layout = QGridLayout()

        self.central_widget = QWidget(self)
        self.central_widget.setLayout(self.central_widget_layout)

        self.setCentralWidget(self.central_widget)

        self.setup_gui_elements()

    def setup_gui_elements(self):
        self.setup_file_browser_window()
        self.setup_settings_window()

        self.setup_workarea_window()

    def setup_workarea_window(self):
        self.workarea_window = PugdebugWorkareaWindow(self)
        self.central_widget_layout.addWidget(self.workarea_window, 0, 1, 1, 1)

    def setup_file_browser_window(self):
        self.file_browser_window = PugdebugFileBrowserWindow(self)
        self.central_widget_layout.addWidget(self.file_browser_window, 0, 0, 1, 1)

    def setup_settings_window(self):
        self.settings_window = PugdebugSettingsWindow(self)
        self.central_widget_layout.addWidget(self.settings_window, 1, 0, 1, 1)


class PugdebugWorkareaWindow(QWidget):

    def __init__(self, parent):
        super(PugdebugWorkareaWindow, self).__init__(parent)

        self.file_viewer = PugdebugFileViewer()
        self.variable_viewer = PugdebugVariableViewer()
        self.stacktrace_viewer = PugdebugStacktraceViewer()
        self.breakpoint_viewer = PugdebugBreakpointViewer()

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.file_viewer, 0, 0, 1, 1)
        layout.addWidget(self.variable_viewer, 0, 1, 1, 1)
        layout.addWidget(self.stacktrace_viewer, 1, 0, 1, 1)
        layout.addWidget(self.breakpoint_viewer, 1, 1, 1, 1)


class PugdebugFileBrowserWindow(QWidget):

    def __init__(self, parent):
        super(PugdebugFileBrowserWindow, self).__init__(parent)

        tree = QTreeView(self)

        model = PugdebugFileBrowser()

        tree.setModel(model)
        tree.setRootIndex(model.start_index)

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(tree, 0, 0, 1, 1)


class PugdebugSettingsWindow(QWidget):

    layout = QFormLayout()

    def __init__(self, parent):
        super(PugdebugSettingsWindow, self).__init__(parent)

        port_number = QSpinBox()
        port_number.setRange(1, 65535)
        port_number.setValue(9000)

        layout = QFormLayout()
        self.setLayout(layout)

        layout.addRow("Port:", port_number)
