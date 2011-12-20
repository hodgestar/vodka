"""
XForms model thingies.
"""


class XFormsModel(object):
    def __init__(self):
        self.bindings = []
        self.instance = None
        self.itext = None


class XFormsBinding(object):
    """
    A constraint on XForms data.

    Binds a set of data keys to an :class:`XFormsType`.
    """


class XFormsType(object):
    """
    A data type.
    """
