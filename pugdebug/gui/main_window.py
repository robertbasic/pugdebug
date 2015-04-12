# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QToolBar, QMenuBar, QDockWidget, QLabel, QAction
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

        self.file_browser = PugdebugFileBrowser()
        self.settings_window = PugdebugSettingsWindow(self)
        self.document_viewer = PugdebugDocumentViewer()
        self.variable_viewer = PugdebugVariableViewer()
        self.breakpoint_viewer = PugdebugBreakpointViewer()
        self.stacktrace_viewer = PugdebugStacktraceViewer()
        self.expression_viewer = PugdebugExpressionViewer()

        self.setCentralWidget(self.document_viewer)

        self.setup_gui_elements()

    def closeEvent(self, event):
        set_setting("window/geometry", self.saveGeometry())
        set_setting("window/state", self.saveState())

        super(PugdebugMainWindow, self).closeEvent(event)

    def setup_gui_elements(self):
        self.setup_fonts()
        self.setup_docks()

        self.setup_actions()
        self.toggle_actions(False)

        self.setup_toolbar()
        self.setup_menubar()
        self.setup_statusbar()

    def setup_statusbar(self):
        self.permanent_statusbar = QLabel("Idle...")
        self.statusBar().addPermanentWidget(self.permanent_statusbar)

    def setup_fonts(self):
        font = QFont('mono')
        font.setStyleHint(QFont.Monospace)
        font.setPixelSize(12)
        self.setFont(font)

    def setup_docks(self):
        self.__add_dock_widget(
            self.file_browser,
            "File Browser",
            Qt.LeftDockWidgetArea
        )

        self.__add_dock_widget(
            self.settings_window,
            "Settings",
            Qt.LeftDockWidgetArea
        )

        self.__add_dock_widget(
            self.variable_viewer,
            "Variables",
            Qt.RightDockWidgetArea
        )

        self.__add_dock_widget(
            self.expression_viewer,
            "Expressions",
            Qt.RightDockWidgetArea
        )

        self.__add_dock_widget(
            self.breakpoint_viewer,
            "Breakpoints",
            Qt.BottomDockWidgetArea
        )

        self.__add_dock_widget(
            self.stacktrace_viewer,
            "Stacktraces",
            Qt.BottomDockWidgetArea
        )

    def setup_actions(self):
        self.start_debug_action = QAction("Start", self)
        self.start_debug_action.setToolTip("Start server (F1)")
        self.start_debug_action.setStatusTip(
            "Start listening to for connections. Shortcut: F1"
        )
        self.start_debug_action.setShortcut(QKeySequence("F1"))

        self.stop_debug_action = QAction("Stop", self)
        self.stop_debug_action.setToolTip("Stop server (F2)")
        self.stop_debug_action.setStatusTip(
            "Stop listening to for connections. Shortcut: F2"
        )
        self.stop_debug_action.setShortcut(QKeySequence("F2"))

        self.detach_debug_action = QAction("Detach", self)
        self.detach_debug_action.setToolTip("Detach from server (F3)")
        self.detach_debug_action.setStatusTip(
            "Stop the debugging session, but let the PHP process end normally."
            " Shortcut: F3"
        )
        self.detach_debug_action.setShortcut(QKeySequence("F3"))

        self.run_debug_action = QAction("Run", self)
        self.run_debug_action.setToolTip("Start/resume the script (F5)")
        self.run_debug_action.setStatusTip(
            "Start or resume the script until a new breakpoint is reached, "
            "or the end of the script is " "reached. Shortcut: F5"
        )
        self.run_debug_action.setShortcut(QKeySequence("F5"))

        self.step_over_action = QAction("Over", self)
        self.step_over_action.setToolTip("Step over the next statement (F6)")
        self.step_over_action.setStatusTip(
            "Step to the next statement, if "
            "there is a function call involved it will break on the statement "
            "after the function call in the same scope as from where the "
            "command was issued. Shortcut: F6"
        )
        self.step_over_action.setShortcut(QKeySequence("F6"))

        self.step_into_action = QAction("In", self)
        self.step_into_action.setToolTip("Step into the next statement (F7)")
        self.step_into_action.setStatusTip(
            "Step to the next statement, if there is a function call involved "
            "it will break on the first statement in that function. "
            "Shortcut: F7"
        )
        self.step_into_action.setShortcut(QKeySequence("F7"))

        self.step_out_action = QAction("Out", self)
        self.step_out_action.setToolTip("Step out of the current scope (F8)")
        self.step_out_action.setStatusTip(
            "Step out of the current scope and breaks on the next statement. "
            "Shortcut: F8"
        )
        self.step_out_action.setShortcut(QKeySequence("F8"))

        self.quit_action = QAction("&Quit", self)
        self.quit_action.setToolTip("Exit the application (Alt+F4)")
        self.quit_action.setStatusTip("Exit the application. Shortcut: Alt+F4")
        self.quit_action.setShortcut(QKeySequence("Alt+F4"))
        self.quit_action.triggered.connect(self.close)

        self.show_file_browser_action = QAction("&File browser", self)
        self.show_file_browser_action.setStatusTip("Show the file browser")
        self.show_file_browser_action.triggered.connect(
            lambda: self.__show_dock_widget("dock-widget-file-browser")
        )

        self.show_settings_action = QAction("&Settings", self)
        self.show_settings_action.setStatusTip("Show settings")
        self.show_settings_action.triggered.connect(
            lambda: self.__show_dock_widget("dock-widget-settings")
        )

        self.show_variables_action = QAction("&Variables", self)
        self.show_variables_action.setStatusTip("Show variables viewer")
        self.show_variables_action.triggered.connect(
            lambda: self.__show_dock_widget("dock-widget-variables")
        )

        self.show_expressions_action = QAction("&Expressions", self)
        self.show_expressions_action.setStatusTip("Show expressions viewer")
        self.show_expressions_action.triggered.connect(
            lambda: self.__show_dock_widget("dock-widget-expressions")
        )

        self.show_breakpoints_action = QAction("&Breakpoints", self)
        self.show_breakpoints_action.setStatusTip("Show breakpoints viewer")
        self.show_breakpoints_action.triggered.connect(
            lambda: self.__show_dock_widget("dock-widget-breakpoints")
        )

        self.show_stack_traces_action = QAction("&Stack Traces", self)
        self.show_stack_traces_action.setStatusTip("Show stack traces viewer")
        self.show_stack_traces_action.triggered.connect(
            lambda: self.__show_dock_widget("dock-widget-stacktraces")
        )

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setObjectName("main-toolbar")

        toolbar.addAction(self.start_debug_action)
        toolbar.addAction(self.stop_debug_action)
        toolbar.addAction(self.detach_debug_action)
        toolbar.addSeparator()
        toolbar.addAction(self.run_debug_action)
        toolbar.addAction(self.step_over_action)
        toolbar.addAction(self.step_into_action)
        toolbar.addAction(self.step_out_action)

        self.addToolBar(toolbar)

    def setup_menubar(self):
        menu_bar = QMenuBar()

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.quit_action)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.show_file_browser_action)
        view_menu.addAction(self.show_settings_action)
        view_menu.addAction(self.show_variables_action)
        view_menu.addAction(self.show_expressions_action)
        view_menu.addAction(self.show_breakpoints_action)
        view_menu.addAction(self.show_stack_traces_action)

        debug_menu = menu_bar.addMenu("&Debug")
        debug_menu.addAction(self.start_debug_action)
        debug_menu.addAction(self.stop_debug_action)
        debug_menu.addAction(self.detach_debug_action)
        debug_menu.addSeparator()
        debug_menu.addAction(self.run_debug_action)
        debug_menu.addAction(self.step_over_action)
        debug_menu.addAction(self.step_into_action)
        debug_menu.addAction(self.step_out_action)

        self.setMenuBar(menu_bar)

    def toggle_actions(self, enabled):
        self.detach_debug_action.setEnabled(enabled)
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

    def __add_dock_widget(self, widget, title, area):
        dw = QDockWidget(title, self)
        object_name = "dock-widget-%s" % title.lower().replace(" ", "-")
        dw.setObjectName(object_name)
        dw.setWidget(widget)
        self.addDockWidget(area, dw)

    def __show_dock_widget(self, name):
        widget = self.findChild(QDockWidget, name)
        widget.show()
