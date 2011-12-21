"""Test for vodka.itext."""

import unittest

from vodka.methanol import fromstring
from vodka.itext import IText, UnknownLanguage, UnknownReference, RefParseError


EXAMPLE1 = """
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


class TestXFormsIText(unittest.TestCase):

    def mk_itext(self, xml):
        elem = fromstring(xml)
        return IText(elem)

    def test_simple_translation(self):
        itext = self.mk_itext(EXAMPLE1)
        eng = itext.translator("eng")
        self.assertEqual(eng("jr:itext('/data/Name:label')"),
                         "Enter your full name")
        self.assertEqual(eng("jr:itext('/data/Name:hint')"),
                         None)

    def test_other_language(self):
        itext = self.mk_itext(EXAMPLE1)
        afr = itext.translator("afr")
        self.assertEqual(afr("jr:itext('/data/Name:label')"),
                         "Gee jou volle naam")
        self.assertEqual(afr("jr:itext('/data/Name:hint')"),
                         None)

    def test_missing_lang(self):
        itext = self.mk_itext(EXAMPLE1)
        self.assertRaises(UnknownLanguage, itext.translator, "zoo")
        self.assertRaises(UnknownLanguage, itext.translation, "zoo",
                          "jr:itext('/data/Name:hint')")

    def test_missing_ref(self):
        itext = self.mk_itext(EXAMPLE1)
        self.assertRaises(UnknownReference, itext.translation, "eng",
                          "jr:itext('/data/Name:unknown')")

    def test_unsupported_ref(self):
        itext = self.mk_itext(EXAMPLE1)
        self.assertRaises(RefParseError, itext.translation, "eng", "bad:ref")
