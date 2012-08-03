"""Test for vodka.xinputs."""

from unittest import TestCase
from xml.etree import ElementTree

from vodka.itext import IText
from vodka.xinputs import XFormsInput, InputInput, Select1Input
from vodka.methanol import xforms


TRANSLATION = """
<itext>
  <translation lang="eng">
    <text id="/data/Name:label">
      <value>Enter your full name</value>
    </text>
    <text id="/data/Name:hint">
      <value/>
    </text>
    <text id="/data/Favourite cheese:label">
      <value>Select your favourite cheese</value>
    </text>
    <text id="/data/Favourite cheese:hint">
      <value/>
    </text>
    <text id="/data/Favourite cheese:option0">
      <value>Gouda</value>
    </text>
    <text id="/data/Favourite cheese:option1">
      <value>Cheddar</value>
    </text>
  </translation>
</itext>
"""

EXAMPLE1 = """
<input xmlns="%(ns)s" ref="/data/Name">
  <label ref="jr:itext('/data/Name:label')"/>
  <hint ref="jr:itext('/data/Name:hint')"/>
</input>
""" % {
'ns': xforms.DEFAULT_NS,
}

EXAMPLE2 = """
<select1 xmlns="%(ns)s" ref="/data/Favourite cheese">
  <label ref="jr:itext('/data/Favourite cheese:label')"/>
  <hint ref="jr:itext('/data/Favourite cheese:hint')"/>
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


class TestInputInput(TestCase):

    def setUp(self):
        itext = IText(ElementTree.fromstring(TRANSLATION))
        self.tr = itext.translator("eng")

    def test_input(self):
        input_elem = ElementTree.fromstring(EXAMPLE1)
        inp = InputInput(None, None, input_elem)
        self.assertEqual("/data/Name", inp.ref)
        self.assertEqual("Enter your full name", inp.get_label(self.tr))
        self.assertEqual(None, inp.get_hint(self.tr))

    def test_from_element(self):
        input_elem = ElementTree.fromstring(EXAMPLE1)
        inp = XFormsInput.from_element(None, None, input_elem)
        self.assertEqual(inp.__class__, InputInput)


class TestSelect1Input(TestCase):

    def setUp(self):
        itext = IText(ElementTree.fromstring(TRANSLATION))
        self.tr = itext.translator("eng")

    def test_valid(self):
        input_elem = ElementTree.fromstring(EXAMPLE2)
        inp = Select1Input(None, None, input_elem)
        self.assertEqual('/data/Favourite cheese', inp.ref)
        self.assertEqual("Select your favourite cheese",
                         inp.get_label(self.tr))
        self.assertEqual(None, inp.get_hint(self.tr))
        self.assertEqual(['gouda', 'cheddar'], inp.get_values(self.tr))

    def test_from_element(self):
        input_elem = ElementTree.fromstring(EXAMPLE2)
        inp = XFormsInput.from_element(None, None, input_elem)
        self.assertEqual(inp.__class__, Select1Input)
