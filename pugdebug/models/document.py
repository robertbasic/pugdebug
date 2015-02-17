# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

from PyQt5.QtCore import QFile, QFileInfo, QIODevice, QTextCodec

class PugdebugDocument():

    path = None

    contents = None
    filename = None

    def __init__(self, path):
        self.path = path

        file = QFile(path)
        fileinfo = QFileInfo(file)

        file.open(QIODevice.ReadOnly)
        data = file.readAll()
        codec = QTextCodec.codecForName('UTF-8')

        self.contents = codec.toUnicode(data)

        self.filename = fileinfo.fileName()
