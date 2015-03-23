# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import os

from PyQt5.QtWidgets import QFileSystemModel

class PugdebugFileBrowser(QFileSystemModel):

    def __init__(self, parent):
        super(PugdebugFileBrowser, self).__init__(parent)

        home_path = os.path.expanduser('~')

        root_path = "%s/www/pugdebug" % home_path

        self.setRootPath(home_path)

        self.start_index = self.index(root_path)

    def get_file_path(self, model_index):
        if not self.isDir(model_index):
            return self.filePath(model_index)
        return None
