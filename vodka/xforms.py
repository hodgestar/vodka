# -*- test-case-name: vodka.tests.test_xforms -*-

"""
XForms document types.

For now, just ODK forms.
"""

from vodka.xmodels import XFormsModel
from vodka.xinputs import XFormsInput
from vodka.methanol import fromanything, html, xforms


class OdkForm(object):
    """
    A form, containing a model and a list of inputs.

    Currently specific to the output of the online ODK builder.
    """

    def __init__(self, source):
        doc = fromanything(source)
        self.title = doc.findtext("%s/%s" % (html.head, html.title))
        self.model = XFormsModel(doc.find("*/" + xforms.model))
        self.inputs = [XFormsInput.from_element(elem)
                       for elem in doc.find(html.body)]
