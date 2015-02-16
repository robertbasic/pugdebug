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

class PugdebugFileBrowserModel(QFileSystemModel):

    def __init__(self):
        super(PugdebugFileBrowserModel, self).__init__()

        home_path = os.path.expanduser('~')

        root_path = "%s/www/pxdebug" % home_path

        self.setRootPath(home_path )

        self.start_index = self.index(root_path)
