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
    translator = form.model.itext.translator(options.lang)

    print "Running '%s' [language: %s]" % (form.title, options.lang)
    print "----"

    for input in form.inputs:
        print translator(input.label_ref)
        print "  Hint:", translator(input.hint_ref)


if __name__ == "__main__":
    options, args = parse_options()
    sys.exit(main(options, args))
