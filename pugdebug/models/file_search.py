# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

from PyQt5.QtCore import QDir
from fuzzywuzzy import fuzz, process, utils


class PugdebugFileSearch():

    def __init__(self, parent, path):
        self.parent = parent
        self.root = path

    def search(self, search_string):
        if len(search_string) < 3:
            return []
        search_results = self.recursive(self.root, search_string, [])
        search_results = sorted(search_results, key=lambda r: r[1], reverse=True)
        search_results = [("(%s) %s" % (r[1], r[0])) for r in search_results]
        search_results = process.extract(search_string, search_results, limit=10, scorer=fuzz.partial_ratio)
        return [r[0] for r in search_results]

    def recursive(self, path, search_string, paths):
        directory = QDir(path)
        directory.setFilter(QDir.Files | QDir.Dirs | QDir.NoDotAndDotDot)
        directory.setSorting(QDir.DirsLast)

        for entry in directory.entryInfoList():
            if (entry.isFile() and
                    self.should_exclude_by_extension(entry.completeSuffix())):
                current_path = entry.filePath()[len(self.root) + 1:]

                score = self.score_path(current_path, search_string)

                paths.append((current_path, score))
                #if self.is_fuzzy(current_path, search_string):
                    #paths.append(current_path)
            elif entry.isDir():
                paths = self.recursive(entry.filePath(), search_string, paths)

        return paths

    def score_path(self, current_path, search_string):
        search_string = utils.full_process(search_string)
        current_path = utils.full_process(current_path)

        weighted_search_strings = self.weight_search_string(search_string)

        current_path = current_path.split(' ')
        path_parts = current_path[:-2]
        file_parts = current_path[-2:-1]
        p = ' '.join(path_parts)
        f = ' '.join(file_parts)

        path_weight = 0.5
        file_weight = 1

        score = 0
        p_score = 0
        f_score = 0

        for w, s in weighted_search_strings:
            p_ratio = fuzz.partial_ratio(s, p)
            f_ratio = fuzz.partial_ratio(s, f)
            pw = path_weight
            if p_ratio == 100:
                pw = 1
            p_score = p_score + (w * p_ratio * pw)
            f_score = f_score + (w * f_ratio * file_weight)
            score = score + p_score + f_score

        return score

    def weight_search_string(self, search_string):
        words = search_string.split(' ')
        words.reverse()
        nw = len(words)

        d = 0
        weighted_words = []
        for word in words:
            weight = 1 - (d / nw)
            weighted_words.append((weight, word))
            d = d + 1

        return weighted_words

    def is_fuzzy(self, current_path, search_string):
        return fuzz.partial_ratio(search_string, current_path) > 50

    def should_exclude_by_extension(self, extension):
        if (extension.find("php") != -1 and
                extension.find("html") == -1 and
                extension.find("xml") == -1 and
                extension.find("phpt") == -1):
            return True
        return False
