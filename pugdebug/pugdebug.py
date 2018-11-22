# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import os

import logging
import signal

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QErrorMessage, QMessageBox

from pugdebug.debugger import PugdebugDebugger
from pugdebug.syntaxer import PugdebugFormatter
from pugdebug.gui.main_window import PugdebugMainWindow
from pugdebug.gui.document import PugdebugDocument
from pugdebug.models.documents import PugdebugDocuments
from pugdebug.models.file_browser import PugdebugFileBrowser
from pugdebug.models.projects import PugdebugProjects
from pugdebug.models.settings import (get_setting, set_setting,
                                      save_settings, has_setting)


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

        self.formatter = PugdebugFormatter()

        # UI elements
        self.main_window = PugdebugMainWindow()
        self.file_browser = self.main_window.get_file_browser()
        self.projects_browser = self.main_window.get_projects_browser()
        self.settings = self.main_window.get_settings()
        self.document_viewer = self.main_window.get_document_viewer()
        self.variable_viewer = self.main_window.get_variable_viewer()
        self.stacktrace_viewer = self.main_window.get_stacktrace_viewer()
        self.breakpoint_viewer = self.main_window.get_breakpoint_viewer()
        self.expression_viewer = self.main_window.get_expression_viewer()

        self.documents = PugdebugDocuments()

        self.setup_file_browser()

        self.setup_projects_browser()

        self.connect_signals()

        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def setup_file_browser(self):
        """Setup the file browser

        Sets the model on the file browser and hides the
        not needed columns.
        """

        project_root = get_setting('path/project_root')
        model = PugdebugFileBrowser(self)
        model.set_path(project_root)

        self.file_browser.setModel(model)
        self.file_browser.setRootIndex(model.start_index)
        self.file_browser.hide_columns()

    def setup_projects_browser(self):
        """Setup the projects browser

        Sets the model on the projects browser.
        """
        model = PugdebugProjects(self)

        self.projects_browser.setModel(model)

    def connect_signals(self):
        """Connect all signals to their slots

        Connect file browser signals, settings signals, document viewer signals
        toolbar action signals, debugger signals.
        """

        self.connect_file_browser_signals()
        self.connect_projects_browser_signals()
        self.connect_search_files_signals()
        self.connect_settings_signals()
        self.connect_document_viewer_signals()
        self.connect_documents_signals()
        self.connect_toolbar_action_signals()
        self.connect_debugger_signals()
        self.connect_expression_viewer_signals()
        self.connect_stacktrace_viewer_signals()
        self.connect_breakpoint_viewer_signals()

    def connect_file_browser_signals(self):
        """Connect file browser signals

        Connects the file browser's activated signal to the
        slot that gets called when a file browser item is activated.
        """
        self.file_browser.activated.connect(self.file_browser_item_activated)

    def connect_projects_browser_signals(self):
        """Connect projects browser signals

        Connects the projects browser's activated signal to the
        slot that gets called when a project browser item is activated.

        Connects the signal that gets emitted from the main window
        when a new project gets created.
        """
        self.projects_browser.activated.connect(
            self.projects_browser_item_activated
        )
        self.main_window.new_project_created_signal.connect(
            self.handle_new_project_created
        )

    def connect_search_files_signals(self):
        """Connect search for files signals

        Connects the signal that is emited when a file search result
        is selected from the search for files dialog.
        """
        self.main_window.search_file_selected_signal.connect(
            self.open_document
        )

    def connect_settings_signals(self):
        """Connect settings signals

        Connects the signal that gets fired when project root gets changed.
        """
        self.settings.settings_changed_signal.connect(
            self.handle_settings_changed
        )

    def connect_document_viewer_signals(self):
        """Connect document viewer signals
        Connects the signal that gets fired when a tab widget is being closed.
        It will call the method that will close the document.
        """
        self.document_viewer.tabCloseRequested.connect(self.close_document)

    def connect_documents_signals(self):
        """Connect documents signals
        Connects the signals that get fired when a document model signal
        happens. Either when a document gets changed, or when a document gets
        removed.
        """
        # Handle when a document gets changed outside of pugdebug
        self.documents.document_changed.connect(
            self.handle_document_changed
        )

        # Handle when a document gets removed outside of pugdebug
        self.documents.document_removed.connect(
            self.handle_document_removed
        )

    def connect_toolbar_action_signals(self):
        """Connect toolbar action signals

        Connect signals that get emitted when the toolbar actions get
        triggered.

        Connect signals when the start/stop debug actions are triggered are
        connected.

        Connect signals when the run and step continuation commands are
        triggered are connected.
        """
        self.main_window.start_listening_action.triggered.connect(
            self.start_listening
        )
        self.main_window.stop_listening_action.triggered.connect(
            self.stop_listening
        )
        self.main_window.stop_debug_action.triggered.connect(self.stop_debug)
        self.main_window.detach_debug_action.triggered.connect(
            self.detach_debug
        )
        self.main_window.run_debug_action.triggered.connect(self.run_debug)
        self.main_window.step_over_action.triggered.connect(self.step_over)
        self.main_window.step_into_action.triggered.connect(self.step_into)
        self.main_window.step_out_action.triggered.connect(self.step_out)

    def connect_debugger_signals(self):
        """Connect debugger signals

        Connecting signals that get emitted when a session starts or stops,
        when a step command is completed, when variables are read, when
        stacktraces are read, when a breakpoint gets removed, when breakpoints
        are read, when one or more expressions are evaluated.

        Connect signal that gets emitted when an error happens during the
        debugging session.
        """

        # Start/stop signals
        self.debugger.server_stopped_signal.connect(
            self.handle_server_stopped_listening
        )
        self.debugger.debugging_started_signal.connect(
            self.handle_debugging_started
        )
        self.debugger.debugging_post_start_signal.connect(
            self.handle_debugging_post_start
        )
        self.debugger.debugging_stopped_signal.connect(
            self.handle_debugging_stopped
        )

        # Step command signals
        self.debugger.step_command_signal.connect(self.handle_step_command)

        # Variables signals
        self.debugger.got_all_variables_signal.connect(
            self.handle_got_all_variables
        )

        # Stacktraces signals
        self.debugger.got_stacktraces_signal.connect(
            self.handle_got_stacktraces
        )

        # Breakpoints signals
        self.debugger.breakpoint_removed_signal.connect(
            self.handle_breakpoint_removed
        )
        self.debugger.breakpoints_listed_signal.connect(
            self.handle_breakpoints_listed
        )

        # Expression signals
        self.debugger.expression_evaluated_signal.connect(
            self.handle_expression_evaluated
        )
        self.debugger.expressions_evaluated_signal.connect(
            self.handle_expressions_evaluated
        )

        # Error signals
        self.debugger.error_signal.connect(
            self.handle_error
        )

    def connect_expression_viewer_signals(self):
        self.expression_viewer.expression_added_signal.connect(
            self.handle_expression_added_or_changed
        )
        self.expression_viewer.expression_changed_signal.connect(
            self.handle_expression_added_or_changed
        )

    def connect_stacktrace_viewer_signals(self):
        self.stacktrace_viewer.item_double_clicked_signal.connect(
            self.jump_to_line_in_file
        )

    def connect_breakpoint_viewer_signals(self):
        self.breakpoint_viewer.item_double_clicked_signal.connect(
            self.jump_to_line_in_file
        )

    def handle_new_project_created(self, project_name):
        """Handle when a new project gets created

        Reload the projects in the projects browser.

        Find the project that was just created and load it.
        """
        logging.debug("Creating new project %s" % project_name)
        self.projects_browser.load_projects()

        project = self.projects_browser.load_project_by_name(project_name)

        if project is not None:
            self.load_project(project)

    def projects_browser_item_activated(self, index):
        """Handle when a projects browser item gets activated

        Find the project and load it.
        """
        project = self.projects_browser.model().get_project_by_index(index)
        self.load_project(project)

    def load_project(self, project):
        """Load a project

        Get the settings for the project and load them as the current
        application settings.

        Set the current project name in the window title.

        Set the current project name setting in application settings.
        """
        project_settings = project.get_settings()

        project_name = project.get_project_name()

        logging.debug("Loading project %s" % project_name)

        set_setting('current_project', project_name)

        changed_settings = save_settings(project_settings)

        self.handle_settings_changed(changed_settings)

        self.main_window.set_window_title(project_name)

    def file_browser_item_activated(self, index):
        """Handle when file browser item gets activated

        Find the path of the activated item and open that document.
        """
        path = self.file_browser.model().get_file_path(index)

        logging.debug("Trying to open path %s" % path)

        if path is not None:
            self.open_document(path, False)

    def open_document(self, path, map_paths=True):
        """Open a document

        If a document is not already open, open it and add it as a new
        tab.

        If the document is already open, focus the tab with that document.

        If the path of the document should be mapped, and the file can't
        be found after mapping, show an error message and stop the debugging
        session.
        """

        path = self.__get_path_mapped_to_local(path, map_paths)

        logging.debug("Opening document for path %s" % path)

        if not self.documents.is_document_open(path):
            logging.debug("Opening new document")
            document_model = self.documents.open_document(path)

            document_widget = PugdebugDocument(
                document_model,
                self.formatter
            )
            # For every new document that gets opened, connect to the double
            # clicked signal of that document
            document_widget.document_double_clicked_signal.connect(
                self.handle_document_double_click
            )

            # Add the newly opened document to the document viewer's tab stack
            self.document_viewer.add_tab(
                document_widget,
                document_model.filename,
                path
            )
        else:
            logging.debug("Focusing opened document")
            # Just focus the tab that has the opened document
            index = self.document_viewer.find_tab_index_by_path(path)
            self.document_viewer.setCurrentIndex(index)

    def handle_document_double_click(self, path, line_number):
        """Handle when a document gets double clicked

        We get the path of the document that was double clicked and the line
        number of the line that was double clicked inside that document.

        If there is no breakpoint set on that line, we set it.
        If there is a breakpoint set on that line, we remove it.
        """
        path = self.__get_path_mapped_to_remote(path)

        logging.debug("Getting a breakpoint on %s:%s" % (path, line_number))

        breakpoint = self.get_breakpoint(path, line_number)

        if breakpoint is None:
            logging.debug("Setting breakpoint")
            breakpoint = {'filename': path, 'lineno': line_number}
            self.set_breakpoint(breakpoint)
        else:
            logging.debug("Removing breakpoint")
            self.remove_breakpoint(breakpoint)

    def handle_document_changed(self, document_model):
        """Handle when a document gets chaned

        Pass on to the document widget the new document model.

        Remove stale breakpoints.
        """
        path = document_model.path

        logging.debug("Document changed: %s" % path)

        document_widget = self.document_viewer.get_document_by_path(path)
        document_widget.handle_document_changed(document_model)

        self.remove_stale_breakpoints(path)

    def handle_document_removed(self, document_model):
        """Handle when a document gets removed outside of pugdebug
        """
        path = document_model.path

        logging.debug("Document removed: %s" % path)

        tab_index = self.document_viewer.find_tab_index_by_path(path)
        self.close_document(tab_index)

    def close_document(self, tab_index):
        """Close a document

        Get the document from the tab.
        Delete the document.
        Remove the tab.
        """
        document_widget = self.document_viewer.get_document(tab_index)
        path = document_widget.get_path()

        logging.debug("Closing document: %s" % path)

        self.documents.close_document(path)
        document_widget.deleteLater()
        self.document_viewer.close_tab(tab_index)

        self.remove_stale_breakpoints(path)

    def focus_current_line(self):
        """Focus the current line

        Focus the line where the debugger stopped in the file
        that is being debugged.
        """
        current_file = self.debugger.get_current_file()
        current_line = self.debugger.get_current_line()

        logging.debug("Focusing current line: %s:%s" % (
            current_file, current_line
        ))

        self.jump_to_line_in_file(current_file, current_line, True)

    def jump_to_line_in_file(self, file, line, is_current=False):
        """Jump to a line in a file.

        Show the document, and scroll to the given line.
        """
        self.open_document(file)

        current = 'current ' if is_current else ''
        logging.debug("Jumping to %sline in file: %s:%s" % (
            current, file, line
        ))

        document_widget = self.document_viewer.get_current_document()
        document_widget.move_to_line(line, is_current)

    def handle_settings_changed(self, changed_settings):
        """Handle when settings have changed.

        Given argument is a set of settings's names which have been changed.
        """
        logging.debug("Settings changed")

        if has_setting('current_project'):
            project_name = get_setting('current_project')

            project = self.projects_browser.load_project_by_name(project_name)

            if project is not None:
                project.set_settings(changed_settings)

        changed_setting_keys = changed_settings.keys()

        if 'path/project_root' in changed_setting_keys:
            self.handle_project_root_changed()

        features = ['debugger/max_depth',
                    'debugger/max_children',
                    'debugger/max_data']

        if any(True for feature in features
               if feature in changed_setting_keys):
            self.handle_debugger_features_changed()

        features = ['editor/tab_width',
                    'editor/font_size']

        if any(True for feature in features
                if feature in changed_setting_keys):
            self.handle_editor_features_changed()

    def handle_project_root_changed(self):
        """Handle when the project root is changed

        Update the file browser's model to the new root.
        """
        project_root = get_setting('path/project_root')

        logging.debug("Project root changed: %s" % project_root)

        model = self.file_browser.model()
        model.set_path(project_root)
        self.file_browser.setModel(model)
        self.file_browser.setRootIndex(model.start_index)

    def handle_debugger_features_changed(self):
        logging.debug("Debugger features changed")
        if self.debugger.is_connected():
            logging.debug("Setting debugger features")
            self.debugger.set_debugger_features()

    def handle_editor_features_changed(self):
        logging.debug("Editor features changed")
        for document in self.document_viewer.get_all_documents():
            document.handle_editor_features_changed()

    def start_listening(self):
        """Start listening to new incomming connections

        Clear the variable viewer.

        Clear the stacktrace viewer.

        Remove all line highlights.

        Start a debugging session.
        """
        logging.debug("Start listening")

        break_at_first_line = int(get_setting('debugger/break_at_first_line'))

        logging.debug("Break at first line: %s" % (
            'Yes' if break_at_first_line != 0 else 'No'
        ))

        start_debugging = True

        if break_at_first_line == 0 and len(self.breakpoints) == 0:
            messageBox = QMessageBox()
            messageBox.setText("There are no breakpoints set and the break at"
                               " first line setting is turned off.")
            messageBox.setInformativeText("Are you sure you want to start"
                                          " debugging?")
            messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            answer = messageBox.exec_()

            if answer == QMessageBox.No:
                start_debugging = False
                logging.debug("Don't start debugging, no breakpoints")

        if start_debugging:
            self.variable_viewer.clear()
            self.stacktrace_viewer.clear()

            self.document_viewer.remove_line_highlights()

            self.debugger.start_listening()
            self.main_window.set_debugging_status(1)

    def handle_debugging_started(self):
        """Handle when debugging starts

        This handle should be called when a new connection is
        established with xdebug.

        When debugging multiple requests, for example ajax requests,
        this should be called for every request, as every request
        has its own connection.

        Sets initial breakpoints, breakpoints that were set before the
        debugging session started.

        Open the index file in the document viewer.
        """
        logging.debug("Debugging started")

        self.main_window.set_debugging_status(3)

        self.main_window.toggle_actions(True)

        # Check if path to index file is correct after mapping it
        index_file = self.debugger.get_index_file()
        path = self.__get_path_mapped_to_local(index_file)

        logging.debug("Index file: %s" % index_file)
        logging.debug("Mapped path: %s" % path)

        if path is False:
            logging.debug("Index file not mapped")
            self.handle_error(
                "File does not exist after mapping. "
                "Is the path map correct?"
            )
            self.stop_debug()
            return

        post_start_data = {
            'breakpoints': self.breakpoints
        }
        self.debugger.post_start_command(post_start_data)

    def handle_debugging_post_start(self):
        """Handle post start debugging

        If the code should not break at first line, run the debugger.
        """
        logging.debug("Post start")
        break_at_first_line = int(get_setting('debugger/break_at_first_line'))

        logging.debug("Break at first line: %s" % (
            'Yes' if break_at_first_line != 0 else 'No'
        ))

        if break_at_first_line == 0:
            self.run_debug()
        else:
            self.step_into()

    def stop_listening(self):
        """Stop listening to connections
        """
        logging.debug("Stop listening")
        self.debugger.stop_listening()

    def handle_server_stopped_listening(self):
        """Handle server stopped listening
        """
        logging.debug("Server stopped listening")
        self.main_window.set_debugging_status(0)

    def stop_debug(self):
        """Stop a debugging session

        If the debugging session has a currently active connection,
        it will stop that connection.

        If there is no active connections, the debugging session will
        tell the server to stop listening to new connections.
        """
        logging.debug("Stop debugging")

        self.debugger.stop_debug()

    def handle_debugging_stopped(self):
        """Handle when debugging stops

        This handler should be called when the connection to
        xdebug is terminated.
        """
        logging.debug("Debugging stopped")

        self.main_window.toggle_actions(False)

        self.main_window.set_debugging_status(2)

        self.expression_viewer.clear_values()

    def detach_debug(self):
        """Detach a debugging session.

        The debugging session will end, but the debuged script
        will terminate normally.
        """
        logging.debug("Detach debugger")
        self.debugger.detach_debug()

    def handle_step_command(self):
        """Handle step command

        This handler should be called when one of the step
        commands is executed and the reply message from xdebug
        is read.

        If the debugger is in a breaking state, focus the current line
        in the current file.

        If the debugger is in a stopping state, stop the debugging session.
        """
        logging.debug("Step command")

        self.main_window.set_debugging_status(3)

        if self.debugger.is_breaking():
            logging.debug("Debugger is breaking")

            self.focus_current_line()

            post_step_data = {
                'expressions': self.expression_viewer.get_expressions()
            }
            self.debugger.post_step_command(post_step_data)
        elif self.debugger.is_stopped():
            logging.debug("Debugger is stopped")
            self.stop_debug()
        elif self.debugger.is_stopping():
            logging.debug("Debugger is stopping")
            self.stop_debug()

    def run_debug(self):
        """Issue a run continuation command on the debugger

        This gets called when the "Run" action button is pressed.
        """
        logging.debug("Run command")
        self.main_window.set_debugging_status(4)

        self.debugger.run_debug()

    def step_over(self):
        """Issue a step over continuation command on the debugger

        This gets called when the "Step over" action button is pressed.
        """
        logging.debug("Step over command")

        self.main_window.set_debugging_status(4)

        self.debugger.step_over()

    def step_into(self):
        """Issue a step into continuation command on the debugger

        This gets called when the "Step into" action button is pressed.
        """
        logging.debug("Step into command")

        self.main_window.set_debugging_status(4)

        self.debugger.step_into()

    def step_out(self):
        """Issue a step out continuation command on the debugger

        This gets called when the "Step out" action button is pressed.
        """
        logging.debug("Step out command")

        self.main_window.set_debugging_status(4)

        self.debugger.step_out()

    def handle_got_all_variables(self, variables):
        """Handle when all variables are retrieved from xdebug

        Set the variables on the variable viewer.
        """
        logging.debug("Setting variables received from debugger")

        self.variable_viewer.set_variables(variables)

    def handle_got_stacktraces(self, stacktraces):
        """Handle when stacktraces are retrieved from xdebug

        Set the stacktraces on the stacktrace viewer.
        """
        logging.debug("Setting stacktraces received from debugger")

        self.stacktrace_viewer.set_stacktraces(stacktraces)

    def set_breakpoint(self, breakpoint):
        """Set a breakpoint

        If there is no active debugging session, add the breakpoint data to
        the breakpoints, highlight the breakpoints on the line
        numbers of the documents, and show them in the breakpoint viewer.

        If there is an active debugging session, tell the debugger to set the
        breakpoint.
        """
        logging.debug("Set a breakpoint")

        if not self.debugger.is_connected():
            logging.debug("Debugger is not connected, appending breakpoint")

            self.breakpoints.append(breakpoint)

            path = breakpoint['filename']
            path = self.__get_path_mapped_to_local(path)

            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

            self.breakpoint_viewer.set_breakpoints(self.breakpoints)

            return

        logging.debug("Setting a breakpoint on the debugger")

        self.debugger.set_breakpoint(breakpoint)

    def remove_breakpoint(self, breakpoint):
        """Remove a breakpoint

        If there is no active debugging session, just remove the breakpoint
        from the breakpoints, rehighlight the line numbers for
        breakpoint markers and update the breakpoint viewer.

        If there is an active debugging session, tell the debugger to remove
        the breakpoint.
        """
        logging.debug("Remove a breakpoint")

        if not self.debugger.is_connected():
            logging.debug("Debugger is not connected, removing breakpoint")

            path = breakpoint['filename']
            line_number = breakpoint['lineno']

            for breakpoint in self.breakpoints:
                if (breakpoint['filename'] == path and
                        breakpoint['lineno'] == line_number):
                    self.breakpoints.remove(breakpoint)

            path = self.__get_path_mapped_to_local(path)

            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

            self.breakpoint_viewer.set_breakpoints(self.breakpoints)

            return

        if 'id' in breakpoint:
            breakpoint_id = int(breakpoint['id'])
            logging.debug("Removing breakpoint: %s" % breakpoint_id)
            self.debugger.remove_breakpoint(breakpoint_id)

    def remove_stale_breakpoints(self, path):
        """Remove stale breakpoints for a file

        Breakpoints get stale when a file gets closed.

        Breakpoints get stale when a file gets changed
        outside of the application.
        """
        remote_path = self.__get_path_mapped_to_remote(path)

        logging.debug("Removing stale breakpoints: %s" % remote_path)

        breakpoints = list(filter(
            lambda breakpoint: breakpoint['filename'] != remote_path,
            self.breakpoints
        ))
        self.breakpoints = breakpoints

        self.breakpoint_viewer.set_breakpoints(breakpoints)

    def handle_breakpoint_removed(self, breakpoint_id):
        """Handle when a breakpoint gets removed

        This slot is called when a breakpoint is removed through the debugger.

        It relists the breakpoints and rehighlights the breakpoint markers
        on the line numbers.
        """
        path = None
        line_number = None

        logging.debug("Breakpoint removed")

        for breakpoint in self.breakpoints:
            if int(breakpoint['id']) == breakpoint_id:
                logging.debug("Found removed breakpoint: %s" % breakpoint_id)

                path = breakpoint['filename']
                line_number = breakpoint['lineno']

                self.debugger.list_breakpoints()

        logging.debug("%s:%s" % (path, line_number))

        if path is not None and line_number is not None:
            path = self.__get_path_mapped_to_local(path)

            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

    def get_breakpoint(self, path, line_number):
        """Get a breakpoint by it's path and line number

        If the breakpoint can be found in the breakpoints from a debugging
        session, return that breakpoint.

        If the breakpoint can be found in the init breakpoints, return that.

        Finally return None.
        """
        for breakpoint in self.breakpoints:
            if (breakpoint['filename'] == path and
                    int(breakpoint['lineno']) == line_number):
                return breakpoint

        return None

    def handle_breakpoints_listed(self, breakpoints):
        """Handle when debugger lists breakpoints

        Show the breakpoints in the breakpoint viewer and rehighlight the
        breakpoint markers.
        """
        logging.debug("Breakpoints listed")

        self.breakpoints = breakpoints

        self.breakpoint_viewer.set_breakpoints(breakpoints)

        for breakpoint in breakpoints:
            path = self.__get_path_mapped_to_local(breakpoint['filename'])
            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

    def handle_expression_evaluated(self, index, result):
        """Handle when an expression is evaluated"""
        logging.debug("Expression evaluated")

        self.expression_viewer.set_evaluated(index, result)

    def handle_expressions_evaluated(self, results):
        """Handle when a list of expressions is evaluated"""
        logging.debug("Expressions evaluated")

        for index, result in enumerate(results):
            self.expression_viewer.set_evaluated(index, result)

    def handle_expression_added_or_changed(self, index, expression):
        """Handle when an expression is added, or an existing one is changed.
        """
        logging.debug("Expression added or modified")

        if self.debugger.is_connected():
            self.debugger.evaluate_expression(index, expression)

    def handle_error(self, error):
        """Handle when an error occurs

        Show the error in an error message window.
        """
        em = QErrorMessage(self.main_window)
        em.showMessage(error)

    def __get_path_mapped_to_local(self, path, map_paths=True):
        """Get a path mapped to local

        Turns a path like /var/www into /home/user/local/path
        """
        path_map = get_setting('path/path_mapping')
        if (len(path_map) > 0 and
                map_paths is True and
                path.find(path_map) == 0):
            path_map = path_map.rstrip('/')
            path = path[len(path_map):]
            path = "%s%s" % (self.file_browser.model().rootPath(), path)

            if not os.path.isfile(path):
                return False

        return path

    def __get_path_mapped_to_remote(self, path):
        """Get a path mapped to remote

        Turns a path like /home/user/local/path to /var/www
        """
        path_map = get_setting('path/path_mapping')
        root_path = self.file_browser.model().rootPath()

        if len(path_map) > 0 and path.find(root_path) == 0:
            path_map = path_map.rstrip('/')
            root_path = root_path.rstrip('/')
            path = path[len(root_path):]
            path = "%s%s" % (path_map, path)

        return path

    def run(self):
        """Run the application!
        """
        self.main_window.show()
