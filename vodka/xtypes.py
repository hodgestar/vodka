# -*- test-case-name: vodka.tests.test_xtypes -*-

"""
XForms data types.
"""


class XFormsTypeMetaclass(type):
    """Metaclass that registers XFormsInput sub-classes."""

    def __init__(cls, type, bases, dict):
        super(XFormsTypeMetaclass, cls).__init__(type, bases, dict)
        tag = dict.get("tag")
        if tag is not None:
            cls.register_subclass(tag, cls)


class XFormsType(object):
    """
    A data type.
    """

    __metaclass__ = XFormsTypeMetaclass
    REGISTRY = {}

    @classmethod
    def register_subclass(cls, tag, othercls):
        cls.REGISTRY[tag] = othercls

    @classmethod
    def from_name(cls, name):
        return cls.REGISTRY[name]()

    def __init__(self, params=None):
        self.params = params or {}
        self.value = None

    def set_value(self, value):
        self.value = self.validate(value)

    def get_value(self):
        return self.value

    def validate(self, value):
        raise NotImplementedError()


class StringType(XFormsType):
    tag = 'string'

    def validate(self, value):
        return value


class IntType(XFormsType):
    tag = 'int'

    def validate(self, value):
        return int(value)


class Select1Type(XFormsType):
    tag = 'select1'

    def validate(self, value):
        return value
