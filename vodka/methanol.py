# -*- test-case-name: vodka.tests.test_xforms -*-

"""
Utilities for fixing ElementTree's namespace assumptions.
"""

import re
from xml.etree.ElementTree import QName
from xml.etree.ElementTree import fromstring as etree_fromstring
from xml.etree.ElementTree import parse as etree_parse
from xml.etree.ElementTree import tostring as etree_tostring


class SemanticNamespace(object):
    """Holder for tag names."""

    def __init__(self, default_ns, other_namespaces):
        self.DEFAULT_NS = default_ns
        self.OTHER_NAMESPACES = other_namespaces

    def __getattr__(self, name):
        return str(QName(self.DEFAULT_NS, name))


html = SemanticNamespace("http://www.w3.org/1999/xhtml", [])
xforms = SemanticNamespace("http://www.w3.org/2002/xforms", [])
openrosa = SemanticNamespace("http://openrosa.org/javarosa", [])


def copy_elem(elem, strip_namespace=False):
    new_elem = etree_fromstring(etree_tostring(elem))
    if strip_namespace:
        for sub_elem in new_elem.getiterator():
            # strip the namespace from the fully qualified tag name
            sub_elem.tag = sub_elem.tag.split('}')[-1]
    return new_elem


def sanitize_namespaces(elem):
    """Change all namespaces to sane defaults."""
    # TODO: for now do nothing
    return elem


def fromstring(source):
    elem = etree_fromstring(source)
    return sanitize_namespaces(elem)


def parse(source):
    elem = etree_parse(source)
    return sanitize_namespaces(elem)


def fromanything(source):
    if isinstance(source, basestring):
        return fromstring(source)
    elif hasattr(source, 'read') and callable(source.read):
        return parse(source)
    # assume it's an Element instance
    return source


_xpath_path = re.compile(r'[/a-zA-Z0-9._-]+')
_xpath_attr = re.compile(r'@[a-zA-Z0-9_-]+')
_xpath_id = re.compile(r"\('[^']+'\)")
_xpath_filter = re.compile(r"\[[^]]+\]")


class LimitedXPathParser(object):
    """This is a very limited XPath parser that assumes a bunch of stuff.

    We need to replace it with a real XPath implementation at some point.
    """

    def __init__(self, xpath_expr):
        self.xpath_expr = xpath_expr
        self.parts = []
        self.parse()

    def parse(self):
        # Assume we start with a path.
        path, expr = self._parse_path(self.xpath_expr)
        self.parts.append(('path', path))

        # We may have an id element on that.
        id_attr, expr = self._parse_id(expr)
        if id_attr is not None:
            self.parts.append(('id', id_attr))

        # And then some more path.
        path, expr = self._parse_path(expr)
        if path is not None:
            self.parts.append(('path', path))

        # There's another selection thing, which we ignore for now.
        filter_bits, expr = self._parse_filter(expr)
        if filter_bits is not None:
            self.parts.append(('filter', filter_bits))

        if expr:
            raise ValueError()

    def _parse_path(self, expr):
        match = _xpath_path.match(expr)
        if match is None:
            return (None, expr)
        return (match.group(0), expr[match.end():])

    def _parse_id(self, expr):
        match = _xpath_id.match(expr)
        if match is None:
            return (None, expr)
        return (match.group(0)[2:-2], expr[match.end():])

    def _parse_filter(self, expr):
        match = _xpath_filter.match(expr)
        if match is None:
            return (None, expr)
        expression_bits = [b.strip()
                           for b in match.group(0)[1:-1].split(' and ')]
        for bit in expression_bits:
            if ' ' in bit:
                raise NotImplementedError()
        return (expression_bits, expr[match.end():])


def _namespace_stripping_findall(nodes, path):
    if path.startswith('/'):
        # Strip off a leading '/' if we have one.
        path = path[1:]
    pathbits = path.split('/')
    for pathbit in pathbits:
        new_nodes = []
        if pathbit == '':
            raise NotImplementedError()
        for node in nodes:
            for n in node.getchildren():
                if n.tag.split('}')[-1] == pathbit:
                    new_nodes.append(n)
        nodes = new_nodes
    return nodes


def find_by_xpath(model, node, xpath_expr):
    parsed_xpath = LimitedXPathParser(xpath_expr)
    nodes = [node]
    for kind, data in parsed_xpath.parts:
        new_nodes = []
        if kind == 'path':
            new_nodes.extend(_namespace_stripping_findall(nodes, data))
        elif kind == 'id':
            for n in nodes:
                if n.get('id') == data:
                    new_nodes.append(n)
        elif kind == 'filter':
            def check_node(n):
                for filter_item in data:
                    tag, data_path = filter_item.split('=')
                    tag_value = n.findtext(getattr(xforms, tag))
                    data_value = model.find(data_path).text
                    if tag_value != data_value:
                        return False
                return True
            for n in nodes:
                if check_node(n):
                    new_nodes.append(n)
        else:
            raise NotImplementedError()
        nodes = new_nodes

    return nodes
