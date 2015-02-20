# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import xml.etree.ElementTree as xml_parser

class PugdebugMessageParser():

    namespace = '{urn:debugger_protocol_v1}'

    def __init__(self):
        pass

    def parse_init_message(self, message):
        init_message = {}

        xml = xml_parser.fromstring(message)

        attribs = ['fileuri', 'idekey']
        init_message = self.get_attribs(xml, attribs, init_message)

        for element in xml.getchildren():
            tag_name = element.tag.replace(self.namespace, '')
            tag_value = element.text

            if len(element.attrib) > 0:
                for attrib in element.attrib:
                    tag_value = tag_value + ' ' + element.attrib[attrib]

            init_message[tag_name] = tag_value

        return init_message

    def parse_continuation_message(self, message):
        continuation_message = {}

        xml = xml_parser.fromstring(message)

        attribs = ['command', 'transaction_id', 'status', 'reason']
        continuation_message = self.get_attribs(xml, attribs, continuation_message)

        if len(xml.getchildren()) == 1:
            attribs = ['filename', 'lineno']
            continuation_message = self.get_attribs(xml[0], attribs, continuation_message)

        return continuation_message

    def get_attribs(self, xml, attribs, result):
        for attrib in (attrib for attrib in xml.attrib if attrib in attribs):
            result[attrib] = xml.attrib[attrib]

        return result
