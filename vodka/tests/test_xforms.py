"""Tests for vodka.xforms."""

import unittest
from StringIO import StringIO

from vodka.xforms import OdkForm

EXAMPLE1 = """
<h:html xmlns="http://www.w3.org/2002/xforms"
        xmlns:h="http://www.w3.org/1999/xhtml"
        xmlns:ev="http://www.w3.org/2001/xml-events"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:jr="http://openrosa.org/javarosa">
  <h:head>
    <h:title>Untitled Form</h:title>
    <model>
      <instance>
        <data id="build_Untitled-Form_1323432952">
          <Name>
            Joe Blogs
          </Name>
        </data>
      </instance>
      <itext>
        <translation lang="eng">
          <text id="/data/Name:label">
            <value>Enter your full name</value>
          </text>
          <text id="/data/Name:hint">
            <value/>
          </text>
        </translation>
      </itext>
      <bind nodeset="/data/Name" type="string" required="true()"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/data/Name">
      <label ref="jr:itext('/data/Name:label')"/>
      <hint ref="jr:itext('/data/Name:hint')"/>
    </input>
  </h:body>
</h:html>
"""


class TestOdkForm(unittest.TestCase):

    def test_create_form_from_string(self):
        odk = OdkForm(EXAMPLE1)
        self.assertEqual(odk.title, "Untitled Form")
        first_input = odk.inputs[0]
        self.assertEqual(first_input.ref, '/data/Name')
        translator = odk.model.itext.translator('eng')
        self.assertEqual(translator("jr:itext('/data/Name:label')"),
                         "Enter your full name")

    def test_create_form_from_fileobj(self):
        fileobj = StringIO(EXAMPLE1)
        odk = OdkForm(fileobj)
        first_input = odk.inputs[0]
        self.assertEqual(first_input.ref, '/data/Name')
