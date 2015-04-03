# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QObject

from pugdebug.debugger import PugdebugDebugger
from pugdebug.syntaxer import PugdebugSyntaxerRules
from pugdebug.gui.main_window import PugdebugMainWindow
from pugdebug.gui.document import PugdebugDocument
from pugdebug.models.documents import PugdebugDocuments
from pugdebug.models.file_browser import PugdebugFileBrowser

class Pugdebug(QObject):

    breakpoints = []

    def __init__(self):
        """Initialize the application

        Initializes all the different parts of the application.

        Creates the PugdebugDebugger object, sets up the application UI,
        connects signals to slots.
        """
        super(Pugdebug, self).__init__()

        self.debugger = PugdebugDebugger()

        self.syntaxer_rules = PugdebugSyntaxerRules()

        self.main_window = PugdebugMainWindow()
        self.file_browser = self.main_window.get_file_browser()
        self.settings = self.main_window.get_settings()
        self.document_viewer = self.main_window.get_document_viewer()
        self.variable_viewer = self.main_window.get_variable_viewer()
        self.breakpoint_viewer = self.main_window.get_breakpoint_viewer()

        self.documents = PugdebugDocuments()

        self.setup_file_browser()

        self.connect_signals()

    def setup_file_browser(self):
        """Setup the file browser

        Sets the model on the file browser and hides the
        not needed columns.
        """

        model = PugdebugFileBrowser(self)
        model.set_path(self.settings.get_project_root())

        self.file_browser.setModel(model)
        self.file_browser.setRootIndex(model.start_index)
        self.file_browser.hide_columns()

    def connect_signals(self):
        """Connect all signals to their slots

        Connect file browser signals, toolbar action signals,
        debugger signals.
        """

        self.connect_file_browser_signals()
        self.connect_settings_signals()
        self.connect_document_viewer_signals()

        self.connect_toolbar_action_signals()

        self.connect_debugger_signals()

    def connect_file_browser_signals(self):
        """Connect file browser signals

        Connects the file browser's activated signal to the
        slot that gets called when a file browser item is activated.
        """
        self.file_browser.activated.connect(self.file_browser_item_activated)

    def connect_settings_signals(self):
        self.settings.project_root.returnPressed.connect(self.project_root_changed)

    def connect_document_viewer_signals(self):
        self.document_viewer.tabCloseRequested.connect(self.close_document)

    def connect_toolbar_action_signals(self):
        """Connect toolbar action signals

        Connect signals that get emitted when the toolbar actions get triggered.

        Connect signals when the start/stop debug actions are triggered are connected.

        Connect signals when the run and step continuation commands are triggered are
        connected.
        """
        self.main_window.start_debug_action.triggered.connect(self.start_debug)
        self.main_window.stop_debug_action.triggered.connect(self.stop_debug)
        self.main_window.run_debug_action.triggered.connect(self.run_debug)
        self.main_window.step_over_action.triggered.connect(self.step_over)
        self.main_window.step_into_action.triggered.connect(self.step_into)
        self.main_window.step_out_action.triggered.connect(self.step_out)

    def connect_debugger_signals(self):
        """Connect debugger signals

        Connect signal that gets emitted when the debugging is started.

        Connect signal that gets emmitted when the debugging is stopped.

        Connect signal that gets emitted when a step command is execute.

        Connect signal that gets emitted when all variables from xdebug are read.
        """

        self.debugger.debugging_started_signal.connect(self.handle_debugging_started)
        self.debugger.debugging_stopped_signal.connect(self.handle_debugging_stopped)
        self.debugger.step_command_signal.connect(self.handle_step_command)
        self.debugger.got_all_variables_signal.connect(self.handle_got_all_variables)
        self.debugger.breakpoint_removed_signal.connect(self.handle_breakpoint_removed)
        self.debugger.breakpoints_listed_signal.connect(self.handle_breakpoints_listed)

    def file_browser_item_activated(self, index):
        """Handle when file browser item gets activated

        Find the path of the activated item and open that document.
        """
        path = self.file_browser.model().get_file_path(index)
        if path is not None:
            self.open_document(path, False)

    def open_document(self, path, map_paths=True):
        """Open a document

        If a document is not already open, open it and add it as a new
        tab.

        If the document is already open, focus the tab with that document.
        """

        path = self.__get_path_mapped_to_local(path, map_paths)

        if not self.documents.is_document_open(path):
            document_model = self.documents.open_document(path)

            document_widget = PugdebugDocument(document_model, self.syntaxer_rules)
            document_widget.document_double_clicked_signal.connect(self.handle_document_double_click)

            self.document_viewer.add_tab(document_widget, document_model.filename, path)
        else:
            self.document_viewer.focus_tab(path)

    def handle_document_double_click(self, path, line_number):
        path = self.__get_path_mapped_to_remote(path)

        breakpoint_id = self.get_breakpoint_id(path, line_number)

        if breakpoint_id is None:
            self.set_breakpoint(path, line_number)
        else:
            self.remove_breakpoint(breakpoint_id)

    def close_document(self, tab_index):
        """Close a document

        Get the document from the tab.
        Delete the document.
        Remove the tab.
        """
        document_widget = self.document_viewer.get_document(tab_index)
        self.documents.close_document(document_widget.get_path())
        document_widget.deleteLater()
        self.document_viewer.close_tab(tab_index)

    def focus_current_line(self):
        """Focus the current line

        Focus the line where the debugger stopped in the file
        that is being debugged.
        """
        current_file = self.debugger.get_current_file()
        current_line = self.debugger.get_current_line()

        self.open_document(current_file)

        document_widget = self.document_viewer.get_current_document()
        document_widget.move_to_line(current_line)

    def project_root_changed(self):
        project_root = self.settings.get_project_root()

        model = self.file_browser.model()
        model.set_path(project_root)
        self.file_browser.setModel(model)
        self.file_browser.setRootIndex(model.start_index)

    def start_debug(self):
        self.variable_viewer.clear()

        self.debugger.start_debug()
        self.main_window.set_statusbar_text("Waiting for connection...")

    def handle_debugging_started(self):
        """Handle when debugging starts

        This handler should be called when the connection to
        xdebug is established and the initial message from xdebug
        is read.

        Issue a step_into command to break at the first line.
        """
        self.main_window.set_statusbar_text("Debugging in progress...")

        self.main_window.toggle_actions(True)

        self.step_into()

    def stop_debug(self):
        if self.debugger.is_connected():
            self.debugger.stop_debug()

    def handle_debugging_stopped(self):
        """Handle when debugging stops

        This handler should be called when the connection to
        xdebug is terminated.
        """
        self.debugger.cleanup()
        self.main_window.toggle_actions(False)

        self.main_window.set_statusbar_text("Debugging stopped...")

    def handle_step_command(self):
        """Handle step command

        This handler should be called when one of the step
        commands is executed and the reply message from xdebug
        is read.

        If the debugger is in a breaking state, focus the current line
        in the current file.

        If the debugger is in a stopping state, stop the debugging session.
        """

        if self.debugger.is_breaking():
            self.focus_current_line()
            self.debugger.get_variables()
        elif self.debugger.is_stopped():
            self.stop_debug()
        elif self.debugger.is_stopping():
            self.stop_debug()

    def run_debug(self):
        self.debugger.run_debug()

    def step_over(self):
        self.debugger.step_over()

    def step_into(self):
        self.debugger.step_into()

    def step_out(self):
        self.debugger.step_out()

    def handle_got_all_variables(self, variables):
        """Handle when all variables are retrieved from xdebug
        """
        self.variable_viewer.set_variables(variables)

    def set_breakpoint(self, path, line_number):
        if not self.debugger.is_connected():
            return

        self.debugger.set_breakpoint(path, line_number)

    def remove_breakpoint(self, breakpoint_id):
        if not self.debugger.is_connected():
            return

        self.debugger.remove_breakpoint(breakpoint_id)

    def handle_breakpoint_removed(self, breakpoint_id):
        path = None
        line_number = None

        for breakpoint in self.breakpoints:
            if int(breakpoint['id']) == breakpoint_id:
                path = breakpoint['filename']
                line_number = breakpoint['lineno']

                self.debugger.list_breakpoints()

        if path is not None and line_number is not None:
            path = self.__get_path_mapped_to_local(path)

            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

    def get_breakpoint_id(self, path, line_number):
        if len(self.breakpoints) == 0:
            return None

        for breakpoint in self.breakpoints:
            if breakpoint['filename'] == path and int(breakpoint['lineno']) == line_number:
                return int(breakpoint['id'])

        return None

    def handle_breakpoints_listed(self, breakpoints):
        self.breakpoints = breakpoints

        self.breakpoint_viewer.set_breakpoints(breakpoints)

        for breakpoint in breakpoints:
            path = self.__get_path_mapped_to_local(breakpoint['filename'])
            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

    def __get_path_mapped_to_local(self, path, map_paths=True):
        path_map = self.settings.get_path_mapping()
        if path_map is not False and map_paths is True and path.index(path_map) == 0:
            path = path[len(path_map):]
            path = "%s%s" % (self.file_browser.model().rootPath(), path)

        return path

    def __get_path_mapped_to_remote(self, path):
        path_map = self.settings.get_path_mapping()
        root_path = self.file_browser.model().rootPath()

        if path_map is not False and path.index(root_path) == 0:
            path = path[len(root_path):]
            path = "%s%s" % (path_map, path)

        return path

    def run(self):
        self.main_window.showMaximized()
