"""Test for vodka.xmodels."""

from unittest import TestCase

from vodka.methanol import fromstring
from vodka.xmodels import XFormsModel


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


class TestXFormsModel(TestCase):

    def test_input(self):
        model_elem = fromstring(EXAMPLE1)
        model = XFormsModel(model_elem)
        self.assertEqual('Joe Blogs',
                         model.instance.find('/data/Name').text.strip())
        translator = model.itext.translator('eng')
        self.assertEqual(translator('jr:itext(id("/data/Name:label"))'),
                         'Enter your full name')
