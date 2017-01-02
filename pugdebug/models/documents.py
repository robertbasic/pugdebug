# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import hashlib
import time

from PyQt5.QtCore import QObject, QFileSystemWatcher, QFileInfo, pyqtSignal

from pugdebug.models.document import PugdebugDocument


class PugdebugDocuments(QObject):

    watcher = None

    open_documents = {}

    document_changed = pyqtSignal(object)

    document_removed = pyqtSignal(object)

    def __init__(self):
        super(PugdebugDocuments, self).__init__()

        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.handle_file_changed)

    def open_document(self, path):
        path_key = self.get_path_key(path)

        document = PugdebugDocument(path)
        self.open_documents[path_key] = document

        self.watcher.addPath(path)

        return document

    def close_document(self, path):
        path_key = self.get_path_key(path)
        self.open_documents.pop(path_key, None)

        self.watcher.removePath(path)

    def refresh_document(self, path):
        """Refresh a document

        Gets called when the file system watcher notices
        a change to an open document.
        """
        path_key = self.get_path_key(path)
        document = self.open_documents[path_key]

        document.read_file(path)

        self.document_changed.emit(document)

    def is_document_open(self, path):
        path_key = self.get_path_key(path)
        return path_key in self.open_documents

    def handle_file_changed(self, path):
        """Handle when a watched file gets changed

        Crazy stuff ahead.

        If a file is modified, some editors (systems?) will first remove
        the file and then write it back to the disk. And for that split
        second, the watcher will drop the file from being watched.

        But then again, maybe that file really got deleted? Who knows?!

        Anyway, when a file gets modified, we sleep a short while to
        see if that file will "get back" and if so, add it back to the
        watcher. If not, we'll assume the file got deleted.
        """
        if not self.__is_path_watched(path):
            fileinfo = QFileInfo(path)

            total_slept = 0
            file_exists = fileinfo.exists()

            while not file_exists:
                sleep_for = 0.1
                total_slept += sleep_for

                if total_slept > 1:
                    break

                time.sleep(sleep_for)
                file_exists = fileinfo.exists()

            if file_exists:
                self.watcher.addPath(path)

                self.refresh_document(path)
            else:
                # file got deleted?
                path_key = self.get_path_key(path)
                document = self.open_documents[path_key]
                self.document_removed.emit(document)
        elif self.__is_path_watched(path):
            self.refresh_document(path)

    def get_path_key(self, path):
        path_key = hashlib.md5(path.encode('utf-8'))
        return path_key.hexdigest()

    def __is_path_watched(self, path):
        return path in self.watcher.files()
