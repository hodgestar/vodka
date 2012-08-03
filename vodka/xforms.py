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
        self._doc = fromanything(source)
        self.title = self._doc.findtext("%s/%s" % (html.head, html.title))
        self._model_elem = self._doc.find("*/" + xforms.model)
        self.model = XFormsModel(self._model_elem)

    def get_inputs(self, instance):
        return [XFormsInput.from_element(instance, self._model_elem, elem)
                for elem in self._doc.find(html.body)]
