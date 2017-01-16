# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__ = "robertbasic"

import os
import xml.etree.ElementTree as xml_parser


class PugdebugMessageParser():

    namespace = '{urn:debugger_protocol_v1}'
    typemap = {}

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

    def parse_typemap_message(self, message):
        xml = xml_parser.fromstring(message)

        typemap = {}

        for item in xml.getchildren():
            language, common = item.attrib['name'], item.attrib['type']
            if language and common:
                typemap[language] = common

        return typemap

    def parse_continuation_message(self, message):
        if not message:
            return {}

        continuation_message = {}

        xml = xml_parser.fromstring(message)

        attribs = ['command', 'transaction_id', 'status', 'reason']
        continuation_message = self.get_attribs(
            xml,
            attribs,
            continuation_message
        )

        if len(xml.getchildren()) == 1:
            attribs = ['filename', 'lineno']
            continuation_message = self.get_attribs(
                xml[0],
                attribs,
                continuation_message
            )

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

    def parse_stacktraces_message(self, message):
        if not message:
            return []

        stacktraces = []

        xml = xml_parser.fromstring(message)

        attribs = ['filename', 'lineno', 'where', 'level']
        for child in xml.getchildren():
            stacktrace = {}
            stacktrace = self.get_attribs(child, attribs, stacktrace)

            stacktraces.append(stacktrace)

        return stacktraces

    def parse_breakpoint_set_message(self, message):
        if not message:
            return False

        xml = xml_parser.fromstring(message)

        if len(xml.getchildren()):
            return False

        return True

    def parse_breakpoint_remove_message(self, message):
        if not message:
            return False

        xml = xml_parser.fromstring(message)

        children = xml.getchildren()

        if len(children) == 1:
            child = children.pop()
            if child.tag.endswith('breakpoint'):
                return int(child.attrib['id'])

        return False

    def parse_breakpoint_list_message(self, message):
        if not message:
            return []

        breakpoints = []

        xml = xml_parser.fromstring(message)

        attribs = ['type', 'filename', 'lineno', 'state', 'id']
        for child in xml.getchildren():
            breakpoint = {}
            breakpoint = self.get_attribs(child, attribs, breakpoint)

            breakpoints.append(breakpoint)

        return breakpoints

    def parse_eval_message(self, message):
        xml = xml_parser.fromstring(message)
        child = xml[0]

        # Detect errors as having an <error> child
        if child.tag.endswith('error'):
            return {
                'type': 'error',
                'value': child[0].text
            }

        return self.get_variable(child)

    def get_variables(self, parent, result):
        for child in parent.getchildren():
            result.append(self.get_variable(child))

        return result

    def get_variable(self, xml):
        attribs = [
            'name',
            'type',
            'encoding',
            'classname',
            'numchildren',
            'size'
        ]
        var = {}
        var = self.get_attribs(xml, attribs, var)
        if self.typemap:
            self.map_type(var)

        numchildren = int(var.get('numchildren', 0))
        if var['type'] in ['array', 'object', 'hash'] or numchildren > 0:
            var['variables'] = self.get_variables(xml, [])
        else:
            var['value'] = xml.text

        return var

    def get_attribs(self, xml, attribs, result):
        for attrib in (attrib for attrib in xml.attrib if attrib in attribs):
            if attrib.startswith('file'):
                result[attrib] = self._parse_file_url(xml.attrib[attrib])
            else:
                result[attrib] = xml.attrib[attrib]

        return result

    def _parse_file_url(self, url):
        """Takes a file:// url and returns the file path.

            On windows, needs to strip 3 slashes, e.g.:
            file:///C:/Users/username/file.php

            On linux needs to strip only 2 slashes, e.g.:
            file:///home/user/file.php
        """
        if os.name == 'nt':
            return url.replace('file:///', '')
        else:
            return url.replace('file://', '')

    def set_typemap(self, typemap):
        self.typemap = typemap

    def map_type(self, variable):
        var_type = variable.get('type')

        if var_type:
            variable['type'] = self.typemap.get(var_type, var_type)
