# -*- test-case-name: vodka.tests.test_xinputs -*-

"""
XForms input implementations.
"""


def get_child(elem, child_tag):
    for child in elem:
        if child.tag == child_tag:
            return child
    return None


def get_child_attr(elem, child_tag, attr):
    child = get_child(elem, child_tag)
    if child is not None:
        return child.get(attr)
    return None


class XFormsInput(object):
    """
    An input mechanism.
    """

    def __init__(self, elem):
        self.elem = elem
        self.ref = elem.get('ref')
        self.label_ref = get_child_attr(elem, 'label', 'ref')
        self.hint_ref = get_child_attr(elem, 'hint', 'ref')


class InputInput(XFormsInput):
    tag = 'input'


class OptionItem(object):
    def __init__(self, elem):
        self.elem = elem
        self.ref = elem.get('ref')
        self.value = get_child(elem, 'value').text
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
