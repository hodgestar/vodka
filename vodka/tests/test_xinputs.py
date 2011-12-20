"""Test for vodka.xinputs."""

from unittest import TestCase
from xml.etree import ElementTree

from vodka.xinputs import XFormsInput, InputInput, Select1Input


EXAMPLE1 = """
<input ref="/data/Name">
  <label ref="jr:itext('/data/Name:label')"/>
  <hint ref="jr:itext('/data/Name:hint')"/>
</input>
"""

EXAMPLE2 = """
<select1 ref="/data/Favourite cheese">
  <label ref="jr:itext('/data/Favourite cheese:label')"/>
  <hint ref="jr:itext('/data/Favourite cheese:hint')"/>
  <item>
    <label ref="jr:itext('/data/Favourite cheese:option0')"/>
    <value>gouda</value>
  </item>
  <item>
    <label ref="jr:itext('/data/Favourite cheese:option1')"/>
    <value>cheddar</value>
  </item>
</select1>
"""


class TestInputInput(TestCase):

    def test_input(self):
        input_elem = ElementTree.fromstring(EXAMPLE1)
        inp = InputInput(input_elem)
        self.assertEqual("/data/Name", inp.ref)
        self.assertEqual("jr:itext('/data/Name:label')", inp.label_ref)
        self.assertEqual("jr:itext('/data/Name:hint')", inp.hint_ref)

    def test_from_element(self):
        input_elem = ElementTree.fromstring(EXAMPLE1)
        inp = XFormsInput.from_element(input_elem)
        self.assertEqual(inp.__class__, InputInput)


class TestSelect1Input(TestCase):

    def test_valid(self):
        input_elem = ElementTree.fromstring(EXAMPLE2)
        inp = Select1Input(input_elem)
        self.assertEqual('/data/Favourite cheese', inp.ref)
        self.assertEqual("jr:itext('/data/Favourite cheese:label')",
                         inp.label_ref)
        self.assertEqual("jr:itext('/data/Favourite cheese:hint')",
                         inp.hint_ref)
        self.assertEqual(['gouda', 'cheddar'], inp.get_values())

    def test_from_element(self):
        input_elem = ElementTree.fromstring(EXAMPLE2)
        inp = XFormsInput.from_element(input_elem)
        self.assertEqual(inp.__class__, Select1Input)
