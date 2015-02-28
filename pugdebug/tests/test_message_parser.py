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

    def test_parse_status_break_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="step_into" transaction_id="1" status="break" reason="ok"><xdebug:message filename="file:///home/robert/www/pxdebug/index.php" lineno="3"></xdebug:message></response>'

        result = self.parser.parse_continuation_message(message)

        expected = {
            'command': 'step_into',
            'transaction_id': '1',
            'status': 'break',
            'reason': 'ok',
            'filename': 'file:///home/robert/www/pxdebug/index.php',
            'lineno': '3'
        }

        self.assertEqual(expected, result)

    def test_parse_status_stopping_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="step_into" transaction_id="28" status="stopping" reason="ok"></response>'

        result = self.parser.parse_continuation_message(message)

        expected = {
            'command': 'step_into',
            'transaction_id': '28',
            'status': 'stopping',
            'reason': 'ok'
        }

        self.assertEqual(expected, result)

    def test_parse_variable_message_context_names(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="context_names" transaction_id="2"><context name="Locals" id="0"></context><context name="Superglobals" id="1"></context></response>'

        result = self.parser.parse_variable_message(message)

        expected = [
            {
                'name': 'Locals',
                'id': '0'
            },
            {
                'name': 'Superglobals',
                'id': '1'
            }
        ]

        self.assertEqual(expected, result)
