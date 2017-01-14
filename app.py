#! python

# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

# Fix for Gtk-CRITICAL issues on Ubuntu
# Turn off that stupid overlay scrollbars
import os
os.environ['LIBOVERLAY_SCROLLBAR'] = '0'

import sys

import logging
from logging.config import fileConfig

from PyQt5.QtWidgets import QApplication
from pugdebug.pugdebug import Pugdebug

if __name__ == "__main__":
    fileConfig('logging.ini')
    logger = logging.getLogger()
    app = QApplication(sys.argv)
    logger.debug('Hello pugdebug!')
    pugdebug = Pugdebug()
    logger.debug('Running pugdebug ...')
    pugdebug.run()
    app.exit(app.exec_())
    logger.debug('Pugdebug finished. Bye!')
