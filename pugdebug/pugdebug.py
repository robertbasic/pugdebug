# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QErrorMessage

from pugdebug.debugger import PugdebugDebugger
from pugdebug.syntaxer import PugdebugFormatter
from pugdebug.gui.main_window import PugdebugMainWindow
from pugdebug.gui.document import PugdebugDocument
from pugdebug.models.documents import PugdebugDocuments
from pugdebug.models.file_browser import PugdebugFileBrowser
from pugdebug.models.settings import get_setting


class Pugdebug(QObject):

    init_breakpoints = []
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
        self.settings = self.main_window.get_settings()
        self.document_viewer = self.main_window.get_document_viewer()
        self.variable_viewer = self.main_window.get_variable_viewer()
        self.stacktrace_viewer = self.main_window.get_stacktrace_viewer()
        self.breakpoint_viewer = self.main_window.get_breakpoint_viewer()
        self.expression_viewer = self.main_window.get_expression_viewer()

        self.documents = PugdebugDocuments()

        self.setup_file_browser()

        self.connect_signals()

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

    def connect_signals(self):
        """Connect all signals to their slots

        Connect file browser signals, settings signals, document viewer signals
        toolbar action signals, debugger signals.
        """

        self.connect_file_browser_signals()
        self.connect_settings_signals()
        self.connect_document_viewer_signals()
        self.connect_toolbar_action_signals()
        self.connect_debugger_signals()
        self.connect_expression_viewer_signals()

    def connect_file_browser_signals(self):
        """Connect file browser signals

        Connects the file browser's activated signal to the
        slot that gets called when a file browser item is activated.
        """
        self.file_browser.activated.connect(self.file_browser_item_activated)

    def connect_settings_signals(self):
        """Connect settings signals

        Connects the signal that gets fired when project root gets changed.
        """
        self.settings.project_root.editingFinished.connect(
            self.handle_project_root_changed
        )

    def connect_document_viewer_signals(self):
        """Connect document viewer signals
        Connects the signal that gets fired when a tab widget is being closed.
        It will call the method that will close the document.
        """
        self.document_viewer.tabCloseRequested.connect(self.close_document)

    def connect_toolbar_action_signals(self):
        """Connect toolbar action signals

        Connect signals that get emitted when the toolbar actions get
        triggered.

        Connect signals when the start/stop debug actions are triggered are
        connected.

        Connect signals when the run and step continuation commands are
        triggered are connected.
        """
        self.main_window.start_debug_action.triggered.connect(self.start_debug)
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

        Connect signal that gets emitted when the debugging is started.

        Connect signal that gets emmitted when the debugging is stopped.

        Connect signal that gets emitted when a step command is execute.

        Connect signal that gets emitted when all variables from xdebug are
        read.
        """

        self.debugger.debugging_started_signal.connect(
            self.handle_debugging_started
        )
        self.debugger.debugging_stopped_signal.connect(
            self.handle_debugging_stopped
        )
        self.debugger.debugging_cancelled_signal.connect(
            self.handle_debugging_stopped
        )
        self.debugger.step_command_signal.connect(self.handle_step_command)
        self.debugger.got_all_variables_signal.connect(
            self.handle_got_all_variables
        )
        self.debugger.got_stacktraces_signal.connect(
            self.handle_got_stacktraces
        )
        self.debugger.breakpoint_removed_signal.connect(
            self.handle_breakpoint_removed
        )
        self.debugger.breakpoints_listed_signal.connect(
            self.handle_breakpoints_listed
        )
        self.debugger.expression_evaluated_signal.connect(
            self.handle_expression_evaluated
        )
        self.debugger.expressions_evaluated_signal.connect(
            self.handle_expressions_evaluated
        )

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

            document_widget = PugdebugDocument(
                document_model,
                self.formatter
            )
            # For every new document that gets opened, connect to the double
            # clicked signal of that document
            document_widget.document_double_clicked_signal.connect(
                self.handle_document_double_click
            )

            # Handle when a document gets changed outside of pugdebug
            self.documents.document_changed.connect(
                self.handle_document_changed
            )

            # Add the newly opened document to the document viewer's tab stack
            self.document_viewer.add_tab(
                document_widget,
                document_model.filename,
                path
            )
        else:
            # Just focus the tab that has the opened document
            self.document_viewer.focus_tab(path)

    def handle_document_double_click(self, path, line_number):
        """Handle when a document gets double clicked

        We get the path of the document that was double clicked and the line
        number of the line that was double clicked inside that document.

        If there is no breakpoint set on that line, we set it.
        If there is a breakpoint set on that line, we remove it.
        """
        path = self.__get_path_mapped_to_remote(path)

        breakpoint = self.get_breakpoint(path, line_number)

        if breakpoint is None:
            breakpoint = {'filename': path, 'lineno': line_number}
            self.set_breakpoint(breakpoint)
        else:
            self.remove_breakpoint(breakpoint)

    def handle_document_changed(self, document_model):
        """Handle when a document gets chaned

        Pass on to the document widget the new document model.

        Remove stale breakpoints.
        """
        path = document_model.path
        document_widget = self.document_viewer.get_document_by_path(path)
        document_widget.handle_document_changed(document_model)

        self.remove_stale_breakpoints(path)

    def close_document(self, tab_index):
        """Close a document

        Get the document from the tab.
        Delete the document.
        Remove the tab.
        """
        document_widget = self.document_viewer.get_document(tab_index)
        path = document_widget.get_path()
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

        self.open_document(current_file)

        document_widget = self.document_viewer.get_current_document()
        document_widget.move_to_line(current_line)

    def handle_project_root_changed(self):
        """Handle when the project root is changed

        Update the file browser's model to the new root.
        """
        project_root = get_setting('path/project_root')

        model = self.file_browser.model()
        model.set_path(project_root)
        self.file_browser.setModel(model)
        self.file_browser.setRootIndex(model.start_index)

    def start_debug(self):
        """Start a new debugging session

        Clear the variable viewer.

        Clear the stacktrace viewer.

        Remove all line highlights.

        Start a debugging session.
        """
        self.variable_viewer.clear()
        self.stacktrace_viewer.clear()

        self.document_viewer.remove_line_highlights()

        self.debugger.start_debug()
        self.main_window.set_statusbar_text("Waiting for connection...")

    def handle_debugging_started(self):
        """Handle when debugging starts

        This handler should be called when the connection to
        xdebug is established and the initial message from xdebug
        is read.

        Sets initial breakpoints, breakpoints that were set before the
        debugging session started.

        Open the index file in the document viewer.
        """
        self.main_window.set_statusbar_text("Debugging in progress...")

        self.main_window.toggle_actions(True)

        self.set_init_breakpoints(self.init_breakpoints)

        self.open_document(self.debugger.get_index_file())

    def stop_debug(self):
        """Stop a debugging session

        Stop the currently active debugging session (if any).
        """
        if self.debugger.is_connected():
            self.debugger.stop_debug()
        elif self.debugger.is_waiting_for_connection():
            self.debugger.cancel_debug()

    def handle_debugging_stopped(self):
        """Handle when debugging stops

        This handler should be called when the connection to
        xdebug is terminated.
        """
        self.debugger.cleanup()

        # Only set breakpoints as init_breakpoints
        # if there are any breakpoints set
        if len(self.breakpoints) > 0:
            self.init_breakpoints = self.breakpoints
            self.breakpoints = []

        self.main_window.toggle_actions(False)

        self.main_window.set_statusbar_text("Debugging stopped...")

        self.expression_viewer.clear_values()

    def detach_debug(self):
        """Detach a debugging session.

        The debugging session will end, but the debuged script
        will terminate normally.
        """
        if self.debugger.is_connected():
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

        if self.debugger.is_breaking():
            self.focus_current_line()

            post_step_data = {
                'expressions': self.expression_viewer.get_expressions()
            }
            self.debugger.post_step_command(post_step_data)
        elif self.debugger.is_stopped():
            self.stop_debug()
        elif self.debugger.is_stopping():
            self.stop_debug()

    def run_debug(self):
        """Issue a run continuation command on the debugger

        This gets called when the "Run" action button is pressed.
        """
        self.debugger.run_debug()

    def step_over(self):
        """Issue a step over continuation command on the debugger

        This gets called when the "Step over" action button is pressed.
        """
        self.debugger.step_over()

    def step_into(self):
        """Issue a step into continuation command on the debugger

        This gets called when the "Step into" action button is pressed.
        """
        self.debugger.step_into()

    def step_out(self):
        """Issue a step out continuation command on the debugger

        This gets called when the "Step out" action button is pressed.
        """
        self.debugger.step_out()

    def handle_got_all_variables(self, variables):
        """Handle when all variables are retrieved from xdebug

        Set the variables on the variable viewer.
        """
        self.variable_viewer.set_variables(variables)

    def handle_got_stacktraces(self, stacktraces):
        """Handle when stacktraces are retrieved from xdebug

        Set the stacktraces on the stacktrace viewer.
        """
        self.stacktrace_viewer.set_stacktraces(stacktraces)

    def set_init_breakpoints(self, breakpoints):
        """Set initial breakpoints

        Initial breakpoints are the breakpoints that are set before a debugging
        session has been started.

        Set initial breakpoints on the debugger. This should be called only
        right after a new debugging session has been started.
        """
        self.debugger.set_init_breakpoints(breakpoints)

    def set_breakpoint(self, breakpoint):
        """Set a breakpoint

        If there is no active debugging session, add the breakpoint data to
        the initial breakpoints, highlight the init breakpoints on the line
        numbers of the documents, and show them in the breakpoint viewer.

        If there is an active debugging session, tell the debugger to set the
        breakpoint.
        """
        if not self.debugger.is_connected():
            self.init_breakpoints.append(breakpoint)

            path = breakpoint['filename']
            path = self.__get_path_mapped_to_local(path)

            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

            self.breakpoint_viewer.set_breakpoints(self.init_breakpoints)

            return

        self.debugger.set_breakpoint(breakpoint)

    def remove_breakpoint(self, breakpoint):
        """Remove a breakpoint

        If there is no active debugging session, just remove the breakpoint
        from the initial breakpoints, rehighlight the line numbers for
        breakpoint markers and update the breakpoint viewer.

        If there is an active debugging session, tell the debugger to remove
        the breakpoint.
        """
        if not self.debugger.is_connected():
            path = breakpoint['filename']
            line_number = breakpoint['lineno']

            for init_breakpoint in self.init_breakpoints:
                if (init_breakpoint['filename'] == path and
                        init_breakpoint['lineno'] == line_number):
                    self.init_breakpoints.remove(init_breakpoint)

            path = self.__get_path_mapped_to_local(path)

            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

            self.breakpoint_viewer.set_breakpoints(self.init_breakpoints)

            return

        breakpoint_id = int(breakpoint['id'])
        self.debugger.remove_breakpoint(breakpoint_id)

    def remove_stale_breakpoints(self, path):
        """Remove stale breakpoints for a file

        Breakpoints get stale when a file gets closed.

        Breakpoints get stale when a file gets changed
        outside of the application.
        """
        remote_path = self.__get_path_mapped_to_remote(path)

        breakpoints = []

        if self.debugger.is_connected():
            breakpoints = list(filter(
                lambda breakpoint: breakpoint['filename'] != remote_path,
                self.breakpoints
            ))
            self.breakpoints = breakpoints
        else:
            breakpoints = list(filter(
                lambda breakpoint: breakpoint['filename'] != remote_path,
                self.init_breakpoints
            ))
            self.init_breakpoints = breakpoints

        self.breakpoint_viewer.set_breakpoints(breakpoints)

    def handle_breakpoint_removed(self, breakpoint_id):
        """Handle when a breakpoint gets removed

        This slot is called when a breakpoint is removed through the debugger.

        It relists the breakpoints and rehighlights the breakpoint markers
        on the line numbers.
        """
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

        for breakpoint in self.init_breakpoints:
            if (breakpoint['filename'] == path and
                    int(breakpoint['lineno']) == line_number):
                return breakpoint

        return None

    def handle_breakpoints_listed(self, breakpoints):
        """Handle when debugger lists breakpoints

        Show the breakpoints in the breakpoint viewer and rehighlight the
        breakpoint markers.
        """
        self.breakpoints = breakpoints

        self.breakpoint_viewer.set_breakpoints(breakpoints)

        for breakpoint in breakpoints:
            path = self.__get_path_mapped_to_local(breakpoint['filename'])
            document_widget = self.document_viewer.get_document_by_path(path)
            document_widget.rehighlight_breakpoint_lines()

    def handle_expression_evaluated(self, index, result):
        """Handle when an expression is evaluated"""
        self.expression_viewer.set_evaluated(index, result)

    def handle_expressions_evaluated(self, results):
        """Handle when a list of expressions is evaluated"""
        for index, result in enumerate(results):
            self.expression_viewer.set_evaluated(index, result)

    def handle_expression_added_or_changed(self, index, expression):
        """Handle when an expression is added, or an existing one is changed.
        """
        if self.debugger.is_connected():
            self.debugger.evaluate_expression(index, expression)

    def handle_error(self, error):
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
            path = path[len(path_map):]
            path = "%s%s" % (self.file_browser.model().rootPath(), path)

        return path

    def __get_path_mapped_to_remote(self, path):
        """Get a path mapped to remote

        Turns a path like /home/user/local/path to /var/www
        """
        path_map = get_setting('path/path_mapping')
        root_path = self.file_browser.model().rootPath()

        if len(path_map) > 0 and path.find(root_path) == 0:
            path = path[len(root_path):]
            path = "%s%s" % (path_map, path)

        return path

    def run(self):
        """Run the application!
        """
        self.main_window.show()
