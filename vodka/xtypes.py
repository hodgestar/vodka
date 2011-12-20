# -*- test-case-name: vodka.tests.test_xtypes -*-

"""
XForms data types.
"""


class XFormsType(object):
    """
    A data type.
    """

    def __init__(self, params=None):
        self.params = params or {}
        self.value = None
        self.setup()

    def set_value(self, value):
        self.value = self.validate(value)

    def get_value(self):
        return self.value

    def setup(self):
        pass

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

    def setup(self):
        self.items = self.params['items']

    def validate(self, value):
        if value not in self.items:
            raise ValueError("Invalid selection.")
        return value
