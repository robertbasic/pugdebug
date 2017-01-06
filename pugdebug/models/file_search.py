# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QDir
from fuzzywuzzy import fuzz


class PugdebugFileSearch():

    def __init__(self, parent, path):
        self.parent = parent
        self.root = path

    def search(self, search_string):
        if len(search_string) < 3:
            return []
        return self.recursive(self.root, search_string, [])

    def recursive(self, path, search_string, paths):
        directory = QDir(path)
        directory.setFilter(QDir.Files | QDir.Dirs | QDir.NoDotAndDotDot)
        directory.setSorting(QDir.DirsLast)

        for entry in directory.entryInfoList():
            if entry.isFile() and entry.completeSuffix().find("php") != -1:
                current_path = entry.filePath()[len(self.root)+1:]

                if self.is_fuzzy(current_path, search_string):
                    paths.append(current_path)
            elif entry.isDir():
                paths = self.recursive(entry.filePath(), search_string, paths)

        return paths

    def is_fuzzy(self, current_path, search_string):
        return fuzz.token_set_ratio(search_string, current_path) > 80
