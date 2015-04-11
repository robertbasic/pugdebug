# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QMdiArea, QMdiSubWindow,
                             QToolBar, QDockWidget, QLabel)
from PyQt5.QtGui import QFont, QKeySequence

from pugdebug.gui.file_browser import PugdebugFileBrowser
from pugdebug.gui.settings import PugdebugSettingsWindow
from pugdebug.gui.documents import PugdebugDocumentViewer
from pugdebug.gui.variables import PugdebugVariableViewer
from pugdebug.gui.stacktraces import PugdebugStacktraceViewer
from pugdebug.gui.breakpoints import PugdebugBreakpointViewer
from pugdebug.gui.expressions import PugdebugExpressionViewer
from pugdebug.models.settings import get_setting, set_setting, has_setting


class PugdebugMainWindow(QMainWindow):

    def __init__(self):
        super(PugdebugMainWindow, self).__init__()
        self.setObjectName("pugdebug")
        self.setWindowTitle("pugdebug")

        if has_setting("window/geometry"):
            self.restoreGeometry(get_setting("window/geometry"))

        if has_setting("window/state"):
            self.restoreState(get_setting("window/state"))

        self.central_widget = QMdiArea(self)
        self.central_widget.tileSubWindows()

        self.setCentralWidget(self.central_widget)

        self.setup_gui_elements()

    def closeEvent(self, event):
        set_setting("window/geometry", self.saveGeometry())
        set_setting("window/state", self.saveState())

        super(PugdebugMainWindow, self).closeEvent(event)

    def setup_gui_elements(self):
        self.setup_fonts()
        self.setup_file_browser_window()
        self.setup_settings_window()

        self.setup_mdi_sub_windows()

        self.setup_toolbar()

        self.setup_statusbar()

    def setup_statusbar(self):
        self.permanent_statusbar = QLabel("Idle...")
        self.statusBar().addPermanentWidget(self.permanent_statusbar)

    def setup_fonts(self):
        font = QFont('mono')
        font.setStyleHint(QFont.Monospace)
        font.setPixelSize(12)
        self.setFont(font)

    def setup_mdi_sub_windows(self):
        self.expression_viewer = PugdebugExpressionViewer()
        self.__add_sub_window(self.expression_viewer, "Expressions")

        self.stacktrace_viewer = PugdebugStacktraceViewer()
        self.__add_sub_window(self.stacktrace_viewer, "Stacktraces")

        self.breakpoint_viewer = PugdebugBreakpointViewer()
        self.__add_sub_window(self.breakpoint_viewer, "Breakpoints")

        self.variable_viewer = PugdebugVariableViewer()
        self.__add_sub_window(self.variable_viewer, "Variables")

        self.document_viewer = PugdebugDocumentViewer()
        self.__add_sub_window(self.document_viewer, "Documents")

    def setup_file_browser_window(self):
        dw = QDockWidget("File Browser", self)
        dw.setObjectName("dock-widget-file-browser")
        self.file_browser = PugdebugFileBrowser()
        dw.setWidget(self.file_browser)
        self.addDockWidget(Qt.LeftDockWidgetArea, dw)

    def setup_settings_window(self):
        dw = QDockWidget("Settings", self)
        dw.setObjectName("dock-widget-settings")
        self.settings_window = PugdebugSettingsWindow(self)
        dw.setWidget(self.settings_window)
        self.addDockWidget(Qt.LeftDockWidgetArea, dw)

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setObjectName("main-toolbar")

        self.start_debug_action = toolbar.addAction("Start")
        self.start_debug_action.setToolTip("Start server (F1)")
        self.start_debug_action.setStatusTip(
            "Start listening to for connections. Shortcut: F1"
        )
        self.start_debug_action.setShortcut(QKeySequence("F1"))

        self.stop_debug_action = toolbar.addAction("Stop")
        self.stop_debug_action.setToolTip("Stop server (F2)")
        self.stop_debug_action.setStatusTip(
            "Stop listening to for connections. Shortcut: F2"
        )
        self.stop_debug_action.setShortcut(QKeySequence("F2"))

        self.run_debug_action = toolbar.addAction("Run")
        self.run_debug_action.setToolTip("Start/resume the script (F5)")
        self.run_debug_action.setStatusTip(
            "Start or resume the script until a new breakpoint is reached, "
            "or the end of the script is " "reached. Shortcut: F5"
        )
        self.run_debug_action.setShortcut(QKeySequence("F5"))

        self.step_over_action = toolbar.addAction("Over")
        self.step_over_action.setToolTip("Step over the next statement (F6)")
        self.step_over_action.setStatusTip(
            "Step to the next statement, if "
            "there is a function call involved it will break on the statement "
            "after the function call in the same scope as from where the "
            "command was issued. Shortcut: F6"
        )
        self.step_over_action.setShortcut(QKeySequence("F6"))

        self.step_into_action = toolbar.addAction("In")
        self.step_into_action.setToolTip("Step into the next statement (F7)")
        self.step_into_action.setStatusTip(
            "Step to the next statement, if there is a function call involved "
            "it will break on the first statement in that function. "
            "Shortcut: F7"
        )
        self.step_into_action.setShortcut(QKeySequence("F7"))

        self.step_out_action = toolbar.addAction("Out")
        self.step_out_action.setToolTip("Step out of the current scope (F8)")
        self.step_out_action.setStatusTip(
            "Step out of the current scope and breaks on the next statement. "
            "Shortcut: F8"
        )
        self.step_out_action.setShortcut(QKeySequence("F8"))

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
        return self.document_viewer

    def get_variable_viewer(self):
        return self.variable_viewer

    def get_stacktrace_viewer(self):
        return self.stacktrace_viewer

    def get_breakpoint_viewer(self):
        return self.breakpoint_viewer

    def get_expression_viewer(self):
        return self.expression_viewer

    def set_statusbar_text(self, text):
        self.permanent_statusbar.setText(text)

    def __add_sub_window(self, widget, title):
        """Add a MDI sub window

        Qt.WA_DeleteOnClose make sure to delete the MDI widget when the
        MDI window is closed.

        Set MDI sub window flags - has a title and min max buttons.

        Set the title of the MDI sub window.
        """
        ms = QMdiSubWindow()
        ms.setWidget(widget)
        ms.setAttribute(Qt.WA_DeleteOnClose)
        self.central_widget.addSubWindow(ms)
        ms.setWindowFlags((
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowMinMaxButtonsHint
        ))
        ms.setWindowTitle(title)
