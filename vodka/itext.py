# -*- test-case-name: vodka.tests.test_itext -*-

"""
XForms itext implementation.

Example itext section::

    <itext>
      <translation lang="eng">
        <text id="/data/Name:label">
          <value>Enter your full name</value>
        </text>
        <text id="/data/Name:hint">
          <value/>
        </text>
      </translation>
      <translation lang="afr">
        <text id="/data/Name:label">
          <value>Gee jou volle naam</value>
        </text>
        <text id="/data/Name:hint">
          <value/>
        </text>
      </translation>
    </itext>

"""


class XFormsIText(object):
    """
    Holds itext data.
    """

    def __init__(self, elem):
        self.elem = elem

    def translation(self, lang, ref):
        pass
