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
        if not message:
            return {}

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
        if not message:
            return {}

        continuation_message = {}

        xml = xml_parser.fromstring(message)

        attribs = ['command', 'transaction_id', 'status', 'reason']
        continuation_message = self.get_attribs(xml, attribs, continuation_message)

        if len(xml.getchildren()) == 1:
            attribs = ['filename', 'lineno']
            continuation_message = self.get_attribs(xml[0], attribs, continuation_message)

        return continuation_message

    def parse_variable_contexts_message(self, message):
        if not message:
            return []

        variable_message = []

        xml = xml_parser.fromstring(message)

        attribs = ['name', 'id']
        for context in xml.getchildren():
            variable_message.append(self.get_attribs(context, attribs, {}))

        return variable_message

    def parse_variables_message(self, message):
        if not message:
            return []

        variables = []

        xml = xml_parser.fromstring(message)

        variables = self.get_variables(xml, variables)

        return variables

    def parse_breakpoint_set_message(self, message):
        if not message:
            return False

        xml = xml_parser.fromstring(message)

        if len(xml.getchildren()):
            return False

        return True

    def parse_breakpoint_list_message(self, message):
        if not message:
            return []

        breakpoints = []

        xml = xml_parser.fromstring(message)

        attribs = ['type', 'filename', 'lineno', 'state']
        for child in xml.getchildren():
            breakpoint = {}
            breakpoint = self.get_attribs(child, attribs, breakpoint)

            breakpoints.append(breakpoint)

        return breakpoints

    def get_variables(self, parent, result):
        attribs = ['name', 'type', 'encoding']
        for child in parent.getchildren():
            var = {}
            var = self.get_attribs(child, attribs, var)

            if var['type'] == 'array':
                var['variables'] = self.get_variables(child, [])
            else:
                var['value'] = child.text

            result.append(var)

        return result

    def get_attribs(self, xml, attribs, result):
        for attrib in (attrib for attrib in xml.attrib if attrib in attribs):
            result[attrib] = xml.attrib[attrib]

        return result
