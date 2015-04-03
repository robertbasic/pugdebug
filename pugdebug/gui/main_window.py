# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QToolBar
from PyQt5.QtGui import QFont

from pugdebug.gui.file_browser import PugdebugFileBrowser
from pugdebug.gui.settings import PugdebugSettingsWindow
from pugdebug.gui.workarea import PugdebugWorkareaWindow


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
        self.setup_fonts()
        self.setup_file_browser_window()
        self.setup_settings_window()

        self.setup_workarea_window()

        self.setup_toolbar()

        self.set_statusbar_text("Idle...")

    def setup_fonts(self):
        font = QFont('mono')
        font.setStyleHint(QFont.Monospace)
        font.setPixelSize(12)
        self.setFont(font)

    def setup_workarea_window(self):
        self.workarea_window = PugdebugWorkareaWindow(self)
        self.central_widget_layout.addWidget(self.workarea_window, 0, 1, 2, 1)

    def setup_file_browser_window(self):
        self.file_browser = PugdebugFileBrowser()
        self.central_widget_layout.addWidget(self.file_browser, 0, 0, 1, 1)

    def setup_settings_window(self):
        self.settings_window = PugdebugSettingsWindow(self)
        self.central_widget_layout.addWidget(self.settings_window, 1, 0, 1, 2)

    def setup_toolbar(self):
        toolbar = QToolBar()

        self.start_debug_action = toolbar.addAction("Start")
        self.stop_debug_action = toolbar.addAction("Stop")
        self.run_debug_action = toolbar.addAction("Run")
        self.step_over_action = toolbar.addAction("Over")
        self.step_into_action = toolbar.addAction("In")
        self.step_out_action = toolbar.addAction("Out")

        self.toggle_actions(False)

        self.addToolBar(toolbar)

    def toggle_actions(self, enabled):
        self.run_debug_action.setEnabled(enabled)
        self.step_over_action.setEnabled(enabled)
        self.step_into_action.setEnabled(enabled)
        self.step_out_action.setEnabled(enabled)

        self.start_debug_action.setEnabled(not enabled)

    def get_file_browser(self):
        return self.file_browser

    def get_settings(self):
        return self.settings_window

    def get_document_viewer(self):
        return self.workarea_window.get_document_viewer()

    def get_variable_viewer(self):
        return self.workarea_window.get_variable_viewer()

    def get_breakpoint_viewer(self):
        return self.workarea_window.get_breakpoint_viewer()

    def set_statusbar_text(self, text):
        self.statusBar().showMessage(text)
