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
    instance = form.model.get_instance()
    renderer = SimpleTextRenderer(translator)

    print "Running '%s' [language: %s]" % (form.title, options.lang)
    print "----"

    for xinput in form.get_inputs(instance):
        print renderer.render(xinput)
        response = raw_input("> ")
        response = renderer.parse(xinput, response)
        form.model.process_input(instance, xinput.ref, response)

    print "----"
    print "Results: "
    print instance.to_xml()


if __name__ == "__main__":
    options, args = parse_options()
    sys.exit(main(options, args))
