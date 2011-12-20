# -*- test-case-name: vodka.tests.test_xmodels -*-

"""
XForms model thingies.
"""

from StringIO import StringIO
from xml.etree import ElementTree

from vodka.methanol import xforms


def make_new_tree(elem, strip_namespace=True):
    xml = StringIO()
    ElementTree.ElementTree(elem).write(xml)
    new_elem = ElementTree.fromstring(xml.getvalue())
    if strip_namespace:
        for sub_elem in new_elem.getiterator():
            # When we get the element here, the namespace has been replaced.
            sub_elem.tag = sub_elem.tag.split('}')[-1]
    return ElementTree.ElementTree(new_elem)


class XFormsModel(object):
    def __init__(self, elem):
        self.bindings = []
        self.instance = make_new_tree(elem.find(xforms.instance))
        self.itext = None


class XFormsBinding(object):
    """
    A constraint on XForms data.

    Binds a set of data keys to an :class:`XFormsType`.
    Elements have the form::
      <bind nodeset="/data/Name" type="string" required="true()"/>
    """

    def __init__(self, elem):
        self.elem = elem
        self.nodeset = elem.get("nodeset")
        self.type = elem.get("type", "string")
        self.required = elem.get("required", "false()")
