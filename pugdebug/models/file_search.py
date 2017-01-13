# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QDir
from fuzzywuzzy import fuzz, process


class PugdebugFileSearch():

    def __init__(self, parent, path):
        self.parent = parent
        self.root = path

    def search(self, search_string):
        if len(search_string) < 3:
            return []
        search_results = self.recursive(self.root, search_string, [])
        search_results = process.extract(search_string, search_results, limit=10)
        return [r[0] for r in search_results]

    def recursive(self, path, search_string, paths):
        directory = QDir(path)
        directory.setFilter(QDir.Files | QDir.Dirs | QDir.NoDotAndDotDot)
        directory.setSorting(QDir.DirsLast)

        for entry in directory.entryInfoList():
            if (entry.isFile() and
                    self.should_exclude_by_extension(entry.completeSuffix())):
                current_path = entry.filePath()[len(self.root) + 1:]

                if self.is_fuzzy(current_path, search_string):
                    paths.append(current_path)
            elif entry.isDir():
                paths = self.recursive(entry.filePath(), search_string, paths)

        return paths

    def is_fuzzy(self, current_path, search_string):
        return fuzz.partial_ratio(search_string, current_path) > 50

    def should_exclude_by_extension(self, extension):
        if (extension.find("php") != -1 and
                extension.find("html") == -1 and
                extension.find("xml") == -1):
            return True
        return False
