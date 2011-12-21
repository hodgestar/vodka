"""Script that runs a XForm form in a text console."""

import sys
from optparse import OptionParser

from vodka.xforms import OdkForm


def parse_options():
    parser = OptionParser()
    parser.add_option("-l", "--lang", dest="lang", default="eng",
                      help="display form in language LANG [default: %default",
                      metavar="LANG")
    return parser.parse_args()


def main(options, args):
    with open(args[0], "rb") as xform_file:
        form = OdkForm(xform_file)
    lang = options.lang

    print "Running '%s' [language: %s]" % (form.title, lang)
    print "----"

    for input in form.inputs:
        print input


if __name__ == "__main__":
    options, args = parse_options()
    sys.exit(main(options, args))
