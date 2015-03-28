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
            'fileuri': '/home/robert/www/pxdebug/index.php',
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
            'filename': '/home/robert/www/pxdebug/index.php',
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

    def test_parse_variable_contexts_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="context_names" transaction_id="2"><context name="Locals" id="0"></context><context name="Superglobals" id="1"></context></response>'

        result = self.parser.parse_variable_contexts_message(message)

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

    def test_parse_variables_simple_local(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="context_get" transaction_id="2;" context="0"><property name="$i" fullname="$i" type="int"><![CDATA[1]]></property></response>'

        result = self.parser.parse_variables_message(message)

        expected = [
            {
                'name': '$i',
                'type': 'int',
                'value': '1'
            }
        ]

        self.assertEqual(expected, result)

    def test_parse_variables_superglobals(self):
        file = open('./pugdebug/tests/_files/superglobals.xml', 'r')
        message = file.read()
        file.close()

        result = self.parser.parse_variables_message(message)

        expected = [
            {
                'name': '$_COOKIE',
                'type': 'array',
                'variables': []
            },
            {
                'name': '$_ENV',
                'type': 'array',
                'variables': []
            },
            {
                'name': '$_FILES',
                'type': 'array',
                'variables': []
            },
            {
                'name': '$_GET',
                'type': 'array',
                'variables': [
                    {
                        'name': 'XDEBUG_SESSION_START',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'MQ=='
                    }
                ]
            },
            {
                'name': '$_POST',
                'type': 'array',
                'variables': []
            },
            {
                'name': '$_REQUEST',
                'type': 'array',
                'variables': [
                    {
                        'name': 'XDEBUG_SESSION_START',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'MQ=='
                    }
                ]
            },
            {
                'name': '$_SERVER',
                'type': 'array',
                'variables': [
                    {
                        'name': 'UNIQUE_ID',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'VlBBajZpYWgxVGtGQGlDVzFuNzhCZ0FBQUFB'
                        },
                    {
                        'name': 'HTTP_HOST',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'bG9jYWxob3N0'
                    },
                    {
                        'name': 'HTTP_USER_AGENT',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'TW96aWxsYS81LjAgKFgxMTsgRmVkb3JhOyBMaW51eCB4ODZfNjQ7IHJ2OjM2LjApIEdlY2tvLzIwMTAwMTAxIEZpcmVmb3gvMzYuMA=='
                        },
                    {
                        'name': 'HTTP_ACCEPT',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'dGV4dC9odG1sLGFwcGxpY2F0aW9uL3hodG1sK3htbCxhcHBsaWNhdGlvbi94bWw7cT0wLjksKi8qO3E9MC44'
                        },
                    {
                        'name': 'HTTP_ACCEPT_LANGUAGE',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'ZW4tVVMsZW47cT0wLjU='
                    },
                    {
                        'name': 'HTTP_ACCEPT_ENCODING',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'Z3ppcCwgZGVmbGF0ZQ=='
                    },
                    {
                        'name': 'HTTP_CONNECTION',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'a2VlcC1hbGl2ZQ=='
                    },
                    {
                        'name': 'PATH',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbg=='
                    },
                    {
                        'name': 'SERVER_SIGNATURE',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': None
                    },
                    {
                        'name': 'SERVER_SOFTWARE',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'QXBhY2hlLzIuNC4xMCAoRmVkb3JhKSBPcGVuU1NMLzEuMC4xay1maXBzIFBIUC81LjYuNg=='
                    },
                    {
                        'name': 'SERVER_NAME',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'bG9jYWxob3N0'
                    },
                    {
                        'name': 'SERVER_ADDR',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'MTI3LjAuMC4x'
                    },
                    {
                        'name': 'SERVER_PORT',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'ODA='
                    },
                    {
                        'name': 'REMOTE_ADDR',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'MTI3LjAuMC4x'
                    },
                    {
                        'name': 'DOCUMENT_ROOT',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'L2hvbWUvcm9iZXJ0L3d3dy9weGRlYnVn'
                    },
                    {
                        'name': 'REQUEST_SCHEME',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'aHR0cA=='
                    },
                    {
                        'name': 'CONTEXT_PREFIX',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': None
                    },
                    {
                        'name': 'CONTEXT_DOCUMENT_ROOT',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'L2hvbWUvcm9iZXJ0L3d3dy9weGRlYnVn'
                    },
                    {
                        'name': 'SERVER_ADMIN',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'd2VibWFzdGVyQGxvY2FsaG9zdA=='
                    },
                    {
                        'name': 'SCRIPT_FILENAME',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'L2hvbWUvcm9iZXJ0L3d3dy9weGRlYnVnL2luZGV4LnBocA=='
                    },
                    {
                        'name': 'REMOTE_PORT',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'NTg3MDI='
                    },
                    {
                        'name': 'GATEWAY_INTERFACE',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'Q0dJLzEuMQ=='
                    },
                    {
                        'name': 'SERVER_PROTOCOL',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'SFRUUC8xLjE='
                    },
                    {
                        'name': 'REQUEST_METHOD',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'R0VU'
                    },
                    {
                        'name': 'QUERY_STRING',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'WERFQlVHX1NFU1NJT05fU1RBUlQ9MQ=='
                    },
                    {
                        'name': 'REQUEST_URI',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'Lz9YREVCVUdfU0VTU0lPTl9TVEFSVD0x'
                    },
                    {
                        'name': 'SCRIPT_NAME',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'L2luZGV4LnBocA=='
                    },
                    {
                        'name': 'PHP_SELF',
                        'type': 'string',
                        'encoding': 'base64',
                        'value': 'L2luZGV4LnBocA=='
                    },
                    {
                        'name': 'REQUEST_TIME_FLOAT',
                        'type': 'float',
                        'value': '1425023978.289'
                    },
                    {
                        'name': 'REQUEST_TIME',
                        'type': 'int',
                        'value': '1425023978'
                    }
                ]
            }
        ]

        self.assertEqual(expected, result)
        self.assertEqual(expected[0], result[0])
        self.assertEqual(expected[1], result[1])
        self.assertEqual(expected[2], result[2])
        self.assertEqual(expected[3], result[3])
        self.assertEqual(expected[4], result[4])
        self.assertEqual(expected[5], result[5])
        self.assertEqual(expected[6]['variables'][28], result[6]['variables'][28])

    def test_parse_successful_breakpoint_set_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="breakpoint_set" transaction_id="9" id="32310001"></response>'

        result = self.parser.parse_breakpoint_set_message(message)

        self.assertTrue(result)

    def test_parse_unsuccessful_breakpoint_set_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="breakpoint_set" transaction_id="9" status="break" reason="ok"><error code="3"><message><![CDATA[invalid or missing options]]></message></error></response>'

        result = self.parser.parse_breakpoint_set_message(message)

        self.assertFalse(result)

    def test_parse_successful_breakpoint_remove_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="breakpoint_remove" transaction_id="11"><breakpoint type="line" filename="file:///home/robert/www/pugdebug/index.php" lineno="10" state="enabled" hit_count="0" hit_value="0" id="41240003"></breakpoint></response>'

        result = self.parser.parse_breakpoint_remove_message(message)

        expected = 41240003

        self.assertEqual(expected, result)

    def test_parse_unsuccessful_breakpoint_remove_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="breakpoint_remove" transaction_id="11" status="break" reason="ok"><error code="205"><message><![CDATA[no such breakpoint]]></message></error></response>'

        result = self.parser.parse_breakpoint_remove_message(message)

        self.assertFalse(result)

    def test_parse_breakpoint_list_message(self):
        message = '<?xml version="1.0" encoding="iso-8859-1"?>\
<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="breakpoint_list" transaction_id="12"><breakpoint type="line" filename="file:///home/robert/www/pugdebug/index.php" lineno="3" state="enabled" hit_count="0" hit_value="0" id="32350002"></breakpoint><breakpoint type="line" filename="file:///home/robert/www/pugdebug/index.php" lineno="10" state="enabled" hit_count="0" hit_value="0" id="32350001"></breakpoint></response>'

        result = self.parser.parse_breakpoint_list_message(message)

        expected = [
            {
                'filename': '/home/robert/www/pugdebug/index.php',
                'id': '32350002',
                'lineno': '3',
                'state': 'enabled',
                'type': 'line'
            },
            {
                'filename': '/home/robert/www/pugdebug/index.php',
                'id': '32350001',
                'lineno': '10',
                'state': 'enabled',
                'type': 'line'
            }
        ]

        self.assertEqual(expected, result)
