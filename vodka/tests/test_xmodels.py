"""Test for vodka.xmodels."""

from unittest import TestCase

from vodka.methanol import fromstring
from vodka.xmodels import XFormsModel, XFormsInstance


EXAMPLE1 = """
<model xmlns="http://www.w3.org/2002/xforms">
  <instance>
    <data id="build_Untitled-Form_1323432952">
      <Name>
        Joe Blogs
      </Name>
      <Cell_number/>
      <Favourite_cheese/>
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
      <text id="/data/Cell_number:label">
        <value>Enter your phone number</value>
      </text>
      <text id="/data/Cell_number:hint">
        <value/>
      </text>
      <text id="/data/Favourite_cheese:label">
        <value>Select your favourite_cheese</value>
      </text>
      <text id="/data/Favourite_cheese:hint">
        <value/>
      </text>
      <text id="/data/Favourite_cheese:option0">
        <value>Gouda</value>
      </text>
      <text id="/data/Favourite_cheese:option1">
        <value>Cheddar</value>
      </text>
    </translation>
  </itext>
  <bind nodeset="/data/Name" type="string" required="true()"/>
  <bind nodeset="/data/Cell_number" type="int"/>
  <bind nodeset="/data/Favourite_cheese" type="select1"/>
</model>
"""

EXAMPLE2 = """
<instance>
  <data id="build_Untitled-Form_1323432952">
    <Name foo="bar">
      Joe Blogs
    </Name>
    <Cell_number/>
    <Favourite_cheese/>
  </data>
</instance>
"""


class TestXFormsModel(TestCase):

    def test_model(self):
        model = XFormsModel(fromstring(EXAMPLE1))
        translator = model.itext.translator('eng')
        self.assertEqual(translator("jr:itext('/data/Name:label')"),
                         "Enter your full name")

    def test_instance(self):
        model = XFormsModel(fromstring(EXAMPLE1))
        instance = model.get_new_instance()
        self.assertEqual('Joe Blogs',
                         instance.find('/data/Name').text.strip())

    def test_elem_path(self):
        get_cpath = XFormsInstance(EXAMPLE2)._get_canonical_path
        self.assertEqual('/data/Name', get_cpath('/data/Name'))
        self.assertEqual('/data/Name', get_cpath('/data/Name/'))
        self.assertEqual(None, get_cpath('/data/foo'))
