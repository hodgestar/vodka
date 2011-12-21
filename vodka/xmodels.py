# -*- test-case-name: vodka.tests.test_xmodels -*-

"""
XForms model thingies.
"""

from copy import deepcopy
from xml.etree.ElementTree import ElementTree, tostring, SubElement

from vodka.methanol import xforms, copy_elem, fromanything
from vodka.itext import IText
from vodka.xtypes import XFormsType


class XFormsInstance(object):
    """
    An xforms data instance.
    """

    def __init__(self, model, source):
        self.model = model
        if isinstance(source, dict):
            self.parse_dict(source)
        else:
            self.parse_xml(source)

    def parse_dict(self, source):
        self.data = deepcopy(source)
        self.doc = ElementTree(fromanything('<instance />'))
        self._parse_dict(self.doc.getroot(), self.data)

    def _parse_dict(self, elem, data):
        for key, value in data.iteritems():
            new_elem = SubElement(elem, key)
            if isinstance(value, dict):
                self._parse_dict(new_elem, value)
            else:
                if value is not None:
                    value = str(value)
                new_elem.text = value

    def parse_xml(self, source):
        # strip namespaces because ODK incorrectly places
        # all its instance sub-elements in the XForms namespace
        elem = copy_elem(fromanything(source), strip_namespace=True)
        self.doc = ElementTree(elem)
        self.data = {}
        self._parse_xml(self.data, self.doc.getroot(), '')

    def _parse_xml(self, data, elem, cpath):
        for child in elem:
            new_cpath = "%s/%s" % (cpath, child.tag)

            if len(child) > 0:
                data[child.tag] = {}
                self._parse_xml(data[child.tag], child, new_cpath)
            else:
                value = child.text
                if value is not None:
                    xtype = self.model.bindings[new_cpath].xtype
                    value = xtype.validate(value)
                data[child.tag] = value

    def to_xml(self):
        return tostring(self.doc.getroot())

    def to_dict(self):
        return deepcopy(self.data)

    def find(self, path):
        return self.doc.find(path)

    def set_data(self, path, value):
        keys = path.strip('/').split('/')
        key = keys.pop()
        data = self.data
        for k in keys:
            data = data[k]
        data[key] = value
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
        for elem in self.elem.findall(xforms.bind):
            cpath = elem.get('nodeset').rstrip('/')
            self.bindings[cpath] = XFormsBinding(elem)

    def get_instance(self, source=None):
        """
        Create a new instance object.
        """
        if source is None:
            source = self.elem.find(xforms.instance)
        return XFormsInstance(self, source)

    def process_input(self, instance, ref, data):
        cpath = instance.get_canonical_path(ref)
        xtype = self.bindings[cpath].xtype
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
