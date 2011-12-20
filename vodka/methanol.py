# -*- test-case-name: vodka.tests.test_xforms -*-

"""
Utilities for fixing ElementTree's namespace assumptions.
"""

from xml.etree.ElementTree import QName
from xml.etree.ElementTree import fromstring as etree_fromstring
from xml.etree.ElementTree import parse as etree_parse


class SemanticNamespace(object):
    """Holder for tag names."""

    def __init__(self, default_ns, other_namespaces):
        self.DEFAULT_NS = default_ns
        self.OTHER_NAMESPACES = other_namespaces

    def __getattr__(self, name):
        return str(QName(self.DEFAULT_NS, name))


html = SemanticNamespace("http://www.w3.org/1999/xhtml", [])
xforms = SemanticNamespace("http://www.w3.org/2002/xforms", [])


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
