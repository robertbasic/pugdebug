# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import sys
import unittest

from pugdebug.message_parser import PugdebugMessageParser

class PugdebugMessageParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = PugdebugMessageParser()

    def test_parse_init_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<init xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" fileuri="file:///home/robert/www/pxdebug/index.php" language="PHP" protocol_version="1.0" appid="3696" idekey="1"><engine version="2.2.7"><![CDATA[Xdebug]]></engine><author><![CDATA[Derick Rethans]]></author><url><![CDATA[http://xdebug.org]]></url><copyright><![CDATA[Copyright (c) 2002-2015 by Derick Rethans]]></copyright></init>'

        result = self.parser.parse_init_message(message)

        expected = {
            'fileuri': 'file:///home/robert/www/pxdebug/index.php',
            'idekey': '1',
            'engine': 'Xdebug 2.2.7',
            'author': 'Derick Rethans',
            'url': 'http://xdebug.org',
            'copyright': 'Copyright (c) 2002-2015 by Derick Rethans'
        }

        self.assertEqual(expected, result)
