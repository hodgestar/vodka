"""Script that runs a XForm form in a text console."""

import sys
from optparse import OptionParser

from vodka.xforms import OdkForm
from vodka.renderers import SimpleTextRenderer


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
    instance = form.model.get_new_instance()
    renderer = SimpleTextRenderer(translator)

    print "Running '%s' [language: %s]" % (form.title, options.lang)
    print "----"

    for input in form.inputs:
        print renderer.render(input)
        response = raw_input("> ")
        response = renderer.parse(input, response)
        form.model.process_input(instance, input, response)

    print "----"
    print "Results: "
    print instance.tostring()


if __name__ == "__main__":
    options, args = parse_options()
    sys.exit(main(options, args))
