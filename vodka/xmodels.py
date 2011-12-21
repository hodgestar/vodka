# -*- test-case-name: vodka.tests.test_xmodels -*-

"""
XForms model thingies.
"""

from xml.etree.ElementTree import ElementTree

from vodka.methanol import xforms, copy_elem
from vodka.itext import IText


class XFormsModel(object):
    def __init__(self, elem):
        self.bindings = []
        # strip namespaces because ODK incorrectly places
        # all its instance sub-elements in the XForms namespace
        instance_elem = copy_elem(elem.find(xforms.instance),
                                  strip_namespace=True)
        self.instance = ElementTree(instance_elem)
        # TODO: the namespace should probably be openrosa
        # but this is the namespace ODK gives it
        self.itext = IText(elem.find(xforms.itext))


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
