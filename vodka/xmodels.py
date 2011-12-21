# -*- test-case-name: vodka.tests.test_xmodels -*-

"""
XForms model thingies.
"""

from xml.etree.ElementTree import ElementTree

from vodka.methanol import xforms, copy_elem, fromanything
from vodka.itext import IText
from vodka.xtypes import XFormsType


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

    def set_data(self, path, value):
        self.find(path).text = str(value)

    def get_canonical_path(self, path):
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
        self._process_bindings()

    def _process_bindings(self):
        self.bindings = {}
        instance = self.get_new_instance()
        for elem in self.elem.findall(xforms.bind):
            cpath = instance.get_canonical_path(elem.get('nodeset'))
            self.bindings[cpath] = XFormsBinding(elem)

    def get_new_instance(self):
        """
        Create a new instance object.
        """
        return XFormsInstance(self.elem.find(xforms.instance))

    def process_input(self, instance, xinput, data):
        cpath = instance.get_canonical_path(xinput.ref)
        xtype = self.bindings[cpath].xtype(xinput.get_type_params())
        instance.set_data(cpath, xtype.validate(data))
        return instance


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
        self.xtype = XFormsType.from_name(elem.get("type", "string"))
        self.required = elem.get("required") == "true()"
