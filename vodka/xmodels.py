# -*- test-case-name: vodka.tests.test_xmodels -*-

"""
XForms model thingies.
"""

from xml.etree.ElementTree import ElementTree

from vodka.methanol import xforms, copy_elem, fromanything
from vodka.itext import IText


class XFormsInstance(object):
    """
    An xforms data instance.
    """

    def __init__(self, source):
        # strip namespaces because ODK incorrectly places
        # all its instance sub-elements in the XForms namespace
        elem = copy_elem(fromanything(source), strip_namespace=True)
        self.doc = ElementTree(elem)

    def find(self, path):
        return self.doc.find(path)

    def _get_canonical_path(self, path):
        if self.find(path) is not None:
            return path.rstrip('/')
        return None


class XFormsModel(object):
    def __init__(self, elem):
        self.elem = elem
        # the namespace should probably be openrosa
        # but ODK shoves it into the XForms namespace
        self.itext = IText(copy_elem(elem.find(xforms.itext),
                                     strip_namespace=True))
        self.bindings = []

    def get_new_instance(self):
        """
        Create a new instance object.
        """
        return XFormsInstance(self.elem.find(xforms.instance))


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
