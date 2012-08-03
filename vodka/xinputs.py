# -*- test-case-name: vodka.tests.test_xinputs -*-

"""
XForms input implementations.
"""

from vodka.methanol import xforms, find_by_xpath


def get_child_attr(elem, child_tag, attr):
    """Utility method for retrieving attributes of child elements"""
    child = elem.find(child_tag)
    if child is not None:
        return child.get(attr)
    return None


def get_translated(translator, elem, ref=None):
    if elem is None:
        return None
    if ref is None:
        ref = elem.get('ref')
    text = None
    if ref is not None:
        if ref.startswith('jr:itext'):
            # This is a translation thing, so translate.
            text = translator(ref, elem)
        else:
            text = elem.findtext(getattr(xforms, ref))
    if text is None:
        text = elem.text
    return text


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

    def __init__(self, instance, model_elem, elem):
        self._instance = instance
        self._model_elem = model_elem
        self.elem = elem
        self.ref = elem.get('ref')
        self.label_elem = elem.find(xforms.label)
        self.hint_elem = elem.find(xforms.hint)
        self.setup_input()

    def get_label(self, translator):
        return get_translated(translator, self.label_elem)

    def get_hint(self, translator):
        return get_translated(translator, self.hint_elem)

    def setup_input(self):
        pass

    def get_type_params(self):
        return {}

    @classmethod
    def register_subclass(cls, tag, othercls):
        cls.REGISTRY[tag] = othercls

    @classmethod
    def from_element(cls, instance, model_elem, elem):
        othercls = cls.REGISTRY[elem.tag]
        return othercls(instance, model_elem, elem)


class InputInput(XFormsInput):
    tag = xforms.input


class OptionItem(object):
    def __init__(self, elem, ref_elem=None):
        self._value_elem = elem.find(xforms.value)
        self._label_elem = elem.find(xforms.label)
        self._value_ref = self._value_elem.get('ref')
        self._label_ref = self._label_elem.get('ref')
        if ref_elem is not None:
            # We're referencing another element here.
            self._value_elem = ref_elem
            self._label_elem = ref_elem

    def get_value(self, translator):
        return get_translated(translator, self._value_elem, self._value_ref)

    def get_label(self, translator):
        return get_translated(translator, self._label_elem, self._label_ref)


class OptionItems(object):
    def __init__(self, instance, model_elem, item_data):
        self._instance = instance
        self._model_elem = model_elem
        self._item_data = item_data
        self._items = None

    def get_items(self):
        if self._items is None:
            self._items = [OptionItem(elem) for elem in self._item_data]
        return self._items


class OptionItemSet(OptionItems):
    def get_items(self):
        if self._items is None:
            self._items = [OptionItem(self._item_data, item)
                           for item in find_by_xpath(
                    self._instance, self._model_elem,
                    self._item_data.get('nodeset'))]
        return self._items


class Select1Input(XFormsInput):
    tag = xforms.select1

    def setup_input(self):
        item_elems = self.elem.findall(xforms.item)
        if item_elems:
            self._items = OptionItems(
                self._instance, self._model_elem, item_elems)
        else:
            self._items = OptionItemSet(
                self._instance, self._model_elem,
                self.elem.find(xforms.itemset))

    def get_items(self):
        return self._items.get_items()

    def get_type_params(self):
        return {'items': self.get_values()}

    def get_values(self, translator):
        return [item.get_value(translator) for item in self.get_items()]
