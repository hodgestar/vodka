"""Tests for vodka.renderers."""

import unittest

from vodka.methanol import fromstring, xforms
from vodka.renderers import SimpleTextRenderer
from vodka.xinputs import InputInput, Select1Input
from vodka.itext import IText


TRANSLATION = """
<itext>
  <translation lang="eng">
    <text id="/data/name:label">
      <value>Enter your full name</value>
    </text>
    <text id="/data/name:hint">
      <value/>
    </text>
    <text id="/data/favourite_cheese:label">
      <value>Select your favourite cheese</value>
    </text>
    <text id="/data/favourite_cheese:hint">
      <value/>
    </text>
    <text id="/data/favourite_cheese:option0">
      <value>Gouda</value>
    </text>
    <text id="/data/favourite_cheese:option1">
      <value>Cheddar</value>
    </text>
  </translation>
</itext>
"""

INPUT = """
<input xmlns="%(ns)s" ref="/data/name">
  <label ref="jr:itext('/data/name:label')"/>
  <hint ref="jr:itext('/data/name:hint')"/>
</input>
""" % {
'ns': xforms.DEFAULT_NS,
}

SELECT1 = """
<select1 xmlns="%(ns)s" ref="/data/favourite_cheese">
  <label ref="jr:itext('/data/favourite_cheese:label')"/>
  <hint ref="jr:itext('/data/favourite_cheese:hint')"/>
  <item>
    <label ref="jr:itext('/data/favourite_cheese:option0')"/>
    <value>gouda</value>
  </item>
  <item>
    <label ref="jr:itext('/data/favourite_cheese:option1')"/>
    <value>cheddar</value>
  </item>
</select1>
""" % {
'ns': xforms.DEFAULT_NS,
}


class TestSimpleTextRenderer(unittest.TestCase):

    def setUp(self):
        itext = IText(fromstring(TRANSLATION))
        translator = itext.translator("eng")
        self.renderer = SimpleTextRenderer(translator)

    def test_input(self):
        inp = InputInput(fromstring(INPUT))
        self.assertEqual(self.renderer.render(inp),
                         "Enter your full name")
        self.assertEqual(self.renderer.parse(inp, "a response"),
                         "a response")

    def test_select1(self):
        select = Select1Input(fromstring(SELECT1))
        self.assertEqual(self.renderer.render(select),
                         "Select your favourite cheese\n1. Gouda\n2. Cheddar")
        self.assertEqual(self.renderer.parse(select, "1"),
                         "gouda")
