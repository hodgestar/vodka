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

import re

from methanol import xforms


class IText(object):
    """
    Holds itext data.
    """

    JR_ITEXT = re.compile(r"jr:itext\(['\"](?P<id>.*)['\"]\)")
    JR_ITEXT_REF = re.compile(r"jr:itext\((?P<path>.*)\)")

    def __init__(self, elem):
        self.translations = {}
        for trans_elem in elem.findall('translation'):
            lang = trans_elem.attrib['lang']
            lookup = {}
            for text in trans_elem.findall('text'):
                xid = text.attrib['id']
                value = text.find('value').text
                lookup[xid] = value
            self.translations[lang] = lookup

    def languages(self):
        """Return a list of supported languages."""
        return sorted(self.translations.keys())

    def translator(self, lang):
        """Return a function that translates references.

        Equivalent to `lambda ref: self.translation(lang, ref)`.
        """
        if lang not in self.translations:
            raise UnknownLanguage("Unknown language: %r" % lang)

        def translation(ref, elem=None):
            return self.translation(lang, ref, elem)
        return translation

    def translation(self, lang, ref, elem=None):
        """Return a translation string for the given language and reference."""
        # First try a direct translation lookup.
        match = self.JR_ITEXT.match(ref)
        if match:
            xid = match.group('id')
        else:
            # Then try an indirect translation lookup.
            match = self.JR_ITEXT_REF.match(ref)
            if not match:
                raise RefParseError("Can't handle ref: %r" % ref)
            xid = elem.findtext(getattr(xforms, match.group('path')))
        lookup = self.translations.get(lang)
        if lookup is None:
            raise UnknownLanguage("Unknown language: %r" % lang)
        if xid not in lookup:
            raise UnknownReference("Unknown reference (language %r): %r"
                                   % (lang, ref))
        return lookup[xid]


class UnknownLanguage(Exception):
    """Raised when a language isn't present in the translations."""


class UnknownReference(Exception):
    """Raised when a reference isn't present in the translations."""


class RefParseError(Exception):
    """Raised when a refernece attribute cannot be interpretted."""
