# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import os
from PyQt5.QtCore import QDir
from fuzzywuzzy import fuzz, process


class PugdebugFileSearch():

    def __init__(self, parent, path):
        self.parent = parent
        self.root = path

    def ignored_paths(self):
        ignored = []
        ignores = []
        ignore_file = "%s/%s" % (self.root, ".gitignore")

        if os.path.exists(ignore_file) and os.path.isfile(ignore_file):
            fd = open(ignore_file)
            ignores = fd.read().rstrip("\n").split("\n")
            fd.close()

        if len(ignores) > 0:
            ignores = list(map(lambda i: self.root + '/' + i, ignores))
            ignored = list(filter(lambda i: os.path.isdir(i), ignores))

        return ignored

    def search(self, search_string):
        if len(search_string) < 3:
            return []

        self.ignored = self.ignored_paths()

        files = self.recursive(self.root, search_string, [])

        scorer = fuzz.token_sort_ratio
        files = process.extract(search_string, files, limit=10, scorer=scorer)

        return [f[0] for f in files]

    def recursive(self, path, search_string, paths):
        directory = QDir(path)
        directory.setFilter(QDir.Files | QDir.Dirs | QDir.NoDotAndDotDot)
        directory.setSorting(QDir.DirsLast)

        for entry in directory.entryInfoList():
            entry_path = entry.absoluteFilePath()
            ignored = self.is_ignored(entry_path)
            if not ignored and entry.isFile() and entry_path.endswith('php'):
                current_path = entry_path[len(self.root) + 1:]

                if self.is_fuzzy(current_path, search_string):
                    paths.append(current_path)
            elif not ignored and entry.isDir():
                paths = self.recursive(entry_path, search_string, paths)

        return paths

    def is_ignored(self, path):
        for ignored in self.ignored:
            if path.startswith(ignored):
                return True
        return False

    def is_fuzzy(self, current_path, search_string):
        return fuzz.partial_ratio(search_string, current_path) > 50
