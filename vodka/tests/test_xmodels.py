"""Test for vodka.xmodels."""

from unittest import TestCase

from vodka.methanol import fromstring, xforms
from vodka.xmodels import XFormsModel, XFormsInstance
from vodka.xinputs import XFormsInput


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

EXAMPLE3 = """
<input xmlns="%(ns)s" ref="/data/Name">
  <label ref="jr:itext('/data/Name:label')"/>
  <hint ref="jr:itext('/data/Name:hint')"/>
</input>
""" % {
'ns': xforms.DEFAULT_NS,
}

EXAMPLE4 = """
<select1 xmlns="%(ns)s" ref="/data/Favourite_cheese">
  <label ref="jr:itext('/data/Favourite_cheese:label')"/>
  <hint ref="jr:itext('/data/Favourite_cheese:hint')"/>
  <item>
    <label ref="jr:itext('/data/Favourite_cheese:option0')"/>
    <value>gouda</value>
  </item>
  <item>
    <label ref="jr:itext('/data/Favourite_cheese:option1')"/>
    <value>cheddar</value>
  </item>
</select1>
""" % {
'ns': xforms.DEFAULT_NS,
}


class TestXFormsModel(TestCase):

    def test_model(self):
        model = XFormsModel(fromstring(EXAMPLE1))
        translator = model.itext.translator('eng')
        self.assertEqual(translator("jr:itext('/data/Name:label')"),
                         "Enter your full name")
        model._process_bindings()

    def test_instance(self):
        model = XFormsModel(fromstring(EXAMPLE1))
        instance = model.get_new_instance()
        self.assertEqual('Joe Blogs',
                         instance.find('/data/Name').text.strip())

    def test_elem_path(self):
        get_cpath = XFormsInstance(EXAMPLE2).get_canonical_path
        self.assertEqual('/data/Name', get_cpath('/data/Name'))
        self.assertEqual('/data/Name', get_cpath('/data/Name/'))
        self.assertEqual(None, get_cpath('/data/foo'))

    def test_input_input(self):
        model = XFormsModel(fromstring(EXAMPLE1))
        instance = model.get_new_instance()
        inp = XFormsInput.from_element(fromstring(EXAMPLE3))
        self.assertEqual('Joe Blogs',
                         instance.find('/data/Name').text.strip())
        model.process_input(instance, inp, "foo")
        self.assertEqual('foo', instance.find('/data/Name').text.strip())

    def test_select1_input(self):
        model = XFormsModel(fromstring(EXAMPLE1))
        instance = model.get_new_instance()
        inp = XFormsInput.from_element(fromstring(EXAMPLE4))
        self.assertEqual(None, instance.find('/data/Favourite_cheese').text)
        model.process_input(instance, inp, "gouda")
        self.assertEqual('gouda', instance.find('/data/Favourite_cheese').text)
