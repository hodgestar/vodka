# -*- test-case-name: vodka.tests.test_renderers -*-

"""
Renderers for XForms.
"""


class FormRenderer(object):
    """Base class for FormRenders."""

    def __init__(self, translator):
        self.translator = translator

    def _input_name(self, input):
        name = input.__class__.__name__.lower()
        if name.endswith("input"):
            name = name[:-len("input")]
        return name

    def _get_render(self, input):
        render_name = "render_%s" % self._input_name(input)
        return getattr(self, render_name, self.render_default)

    def _get_parse(self, input):
        parser_name = "parse_%s" % self._input_name(input)
        return getattr(self, parser_name, self.parse_default)

    def render(self, input):
        """Return text for an input."""
        render_func = self._get_render(input)
        return render_func(input)

    def parse(self, input, response):
        """Parse text response for the given input."""
        parse_func = self._get_parse(input)
        return parse_func(input, response)

    def render_default(self, input):
        raise NotImplementedError("Sub-classes should implement "
                                  "render_default")

    def parse_default(self, input, response):
        raise NotImplementedError("Sub-classes should implement "
                                  "parse_default")


class SimpleTextRenderer(FormRenderer):
    """Renders inputs to simple text."""

    def render_default(self, input):
        text = input.get_label(self.translator)
        hint = input.get_hint(self.translator)
        if hint:
            return "%s\n  Hint: %s" % (text, hint)
        else:
            return text

    def parse_default(self, input, response):
        return response

    def render_select1(self, input):
        lines = [self.render_default(input)]
        for i, item in enumerate(input.get_items()):
            lines.append("%d. %s" % (i + 1, item.get_label(self.translator)))
        return "\n".join(lines)

    def parse_select1(self, input, response):
        i = int(response) - 1
        return input.get_items()[i].get_value(self.translator)
