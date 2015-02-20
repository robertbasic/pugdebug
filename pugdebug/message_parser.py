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

        for attrib in (attrib for attrib in xml.attrib if attrib in ['fileuri', 'idekey']):
            init_message[attrib] = xml.attrib[attrib]

        for element in xml.getchildren():
            tag_name = element.tag.replace(self.namespace, '')
            tag_value = element.text

            if len(element.attrib) > 0:
                for attrib in element.attrib:
                    tag_value = tag_value + ' ' + element.attrib[attrib]

            init_message[tag_name] = tag_value

        return init_message
