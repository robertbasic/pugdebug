#! python

# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import sys

from pugdebug.pugdebug import Pugdebug

if __name__ == "__main__":
    pugdebug = Pugdebug(sys.argv)
    pugdebug.run()
