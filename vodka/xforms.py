# -*- test-case-name: vodka.tests.test_xforms -*-

"""
XForms document types.

For now, just ODK forms.
"""

from vodka.xmodels import XFormsModel
from vodka.xinputs import XFormsInput
from vodka.methanol import fromstring, parse, html, xforms


class OdkForm(object):
    """
    A form, containing a model and a list of inputs.

    Currently specific to the output of the online ODK builder.
    """

    def __init__(self, source):
        if isinstance(source, basestring):
            doc = fromstring(source)
        elif hasattr(source, 'read') and callable(source.read):
            doc = parse(source)
        else:
            # assume it's an Element instance
            doc = source
        self.model = XFormsModel(doc.find("*/" + xforms.model))
        self.inputs = [XFormsInput.from_element(elem)
                       for elem in doc.find(html.body)]
