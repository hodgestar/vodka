# -*- test-case-name: vodka.tests.test_xinputs -*-

"""
XForms input implementations.
"""


def get_child_attr(elem, child_tag, attr):
    """Utility method for retrieving attributes of child elements"""
    child = elem.find(child_tag)
    if child is not None:
        return child.get(attr)
    return None


class XFormsInputMetaclass(type):
    """Metaclass that registers XFormsInput sub-classes."""

    def __init__(cls, type, bases, dict):
        super(XFormsInputMetaclass, cls).__init__(type, bases, dict)
        tag = dict.get("tag")
        if tag is not None:
            cls.register_subclass(tag, cls)


class XFormsInput(object):
    """
    An input mechanism.
    """

    __metaclass__ = XFormsInputMetaclass
    REGISTRY = {}

    def __init__(self, elem):
        self.elem = elem
        self.ref = elem.get('ref')
        self.label_ref = get_child_attr(elem, 'label', 'ref')
        self.hint_ref = get_child_attr(elem, 'hint', 'ref')

    @classmethod
    def register_subclass(cls, tag, othercls):
        cls.REGISTRY[tag] = othercls

    @classmethod
    def from_element(cls, elem):
        othercls = cls.REGISTRY[elem.tag]
        return othercls(elem)


class InputInput(XFormsInput):
    tag = 'input'


class OptionItem(object):
    def __init__(self, elem):
        self.elem = elem
        self.ref = elem.get('ref')
        self.value = elem.findtext('value')
        self.label_ref = get_child_attr(elem, 'label', 'ref')


class Select1Input(XFormsInput):
    tag = 'select1'

    def __init__(self, elem):
        super(Select1Input, self).__init__(elem)
        self.items = []
        for child in elem:
            if child.tag == 'item':
                self.items.append(OptionItem(child))

    def get_values(self):
        return [item.value for item in self.items]
