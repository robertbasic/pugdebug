# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import hashlib

from pugdebug.models.document import PugdebugDocument


class PugdebugDocuments():

    open_documents = {}

    def __init__(self):
        pass

    def open_document(self, path):
        path_key = self.get_path_key(path)
        self.open_documents[path_key] = path

        document = PugdebugDocument(path)

        return document

    def close_document(self, path):
        path_key = self.get_path_key(path)
        self.open_documents.pop(path_key, None)

    def is_document_open(self, path):
        path_key = self.get_path_key(path)
        return path_key in self.open_documents

    def get_path_key(self, path):
        path_key = hashlib.md5(path.encode('utf-8'))
        return path_key.hexdigest()
