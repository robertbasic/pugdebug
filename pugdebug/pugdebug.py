# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import sys

from pugdebug.debugger import PugdebugDebugger
from pugdebug.gui.main_window import PugdebugMainWindow
from pugdebug.gui.document import PugdebugDocument
from pugdebug.models.documents import PugdebugDocuments
from pugdebug.models.file_browser import PugdebugFileBrowser

class Pugdebug():

    def __init__(self):
        """Initialize the application

        Initializes all the different parts of the application.

        Creates the PugdebugDebugger object, sets up the application UI,
        connects signals to slots.
        """

        self.debugger = PugdebugDebugger()

        self.main_window = PugdebugMainWindow()
        self.file_browser = self.main_window.get_file_browser()
        self.document_viewer = self.main_window.get_document_viewer()

        self.documents = PugdebugDocuments()

        self.setup_file_browser()

        self.connect_signals()

    def setup_file_browser(self):
        """Setup the file browser

        Sets the model on the file browser and hides the
        not needed columns.
        """

        model = PugdebugFileBrowser(self.main_window)
        self.file_browser.setModel(model)
        self.file_browser.setRootIndex(model.start_index)
        self.file_browser.hide_columns()

    def connect_signals(self):
        """Connect all signals to their slots

        Connect file browser signals, toolbar action signals,
        debugger signals.
        """

        self.connect_file_browser_signals()

        self.connect_toolbar_action_signals()

        self.connect_debugger_signals()

    def connect_file_browser_signals(self):
        """Connect file browser signals

        Connects the file browser's activated signal to the
        slot that gets called when a file browser item is activated.
        """
        self.file_browser.activated.connect(self.file_browser_item_activated)

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

        Connect signal that gets emitted when the debugging is started, when the TCP connection
        is established and the initial message from xdebug is read.

        Connect signal that gets emitted when a step command is executed and the reply message
        from xdebug is read.
        """

        self.debugger.debugging_started_signal.connect(self.handle_debugging_started)
        self.debugger.step_command_signal.connect(self.handle_step_command)

    def file_browser_item_activated(self, index):
        """Handle when file browser item gets activated

        Find the path of the activated item and open that document.
        """
        path = self.file_browser.model().filePath(index)
        self.open_document(path)

    def open_document(self, path):
        """Open a document

        If a document is not already open, open it and add it as a new
        tab.

        If the document is already open, focus the tab with that document.
        """
        if not self.documents.is_document_open(path):
            document = self.documents.open_document(path)

            doc = PugdebugDocument(document.contents)

            self.document_viewer.add_tab(doc, document.filename, path)
        else:
            self.document_viewer.focus_tab(path)

    def focus_current_line(self):
        """Focus the current line

        Focus the line where the debugger stopped in the file
        that is being debugged.
        """
        current_file = self.debugger.get_current_file()
        current_line = self.debugger.get_current_line()

        self.open_document(current_file)

        doc = self.document_viewer.get_current_document()
        doc.move_to_line(current_line)

    def handle_debugging_started(self):
        """Handle when debugging starts

        This handler should be called when the connection to
        xdebug is established and the initial message from xdebug
        is read.

        Issue a step_into command to break at the first line.
        """
        self.main_window.set_statusbar_text("Debugging in progress...")

        self.focus_current_line()

        self.step_into()

    def start_debug(self):
        self.debugger.start_debug()
        self.main_window.set_statusbar_text("Waiting for connection...")

    def stop_debug(self):
        self.debugger.stop_debug()

        self.main_window.set_statusbar_text("Debugging stopped...")

    def handle_step_command(self):
        """Handle step command

        This handler should be called when one of the step
        commands is executed and the reply message from xdebug
        is read.
        """

        if self.debugger.is_breaking():
            self.focus_current_line()
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

    def run(self):
        self.main_window.showMaximized()
