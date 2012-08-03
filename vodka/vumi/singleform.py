# -*- test-case-name: vodka.vumi.tests.test_singleform -*-

"""
Vumi ApplicationWorker that serves a single form.
"""

import json

from twisted.internet.defer import inlineCallbacks, returnValue

from vumi.application import ApplicationWorker
from vumi.components.session import SessionManager

from vodka.xforms import OdkForm
from vodka.renderers import SimpleTextRenderer


class FormHandler(object):
    """Processes user interactions with a form."""

    STATES = STATE_NEW, STATE_QUESTION, STATE_DONE = [
        "new", "question", "done",
        ]

    def __init__(self, user_id, xform, session):
        self.user_id = user_id
        self.xform = xform
        self.lang = session.get("lang", None)
        self.state = session.get("state", self.STATE_NEW)
        self.shown_before = session.get("shown_before", False)
        self.input_idx = session.get("input_idx", 0)
        data = session.get("instance")
        self.instance = self.xform.model.get_instance(data)

    def set_question(self, input_idx):
        if 0 <= input_idx < len(self.xform.get_inputs(self.instance)):
            self.state = self.STATE_QUESTION
            self.shown_before = False
            self.input_idx = input_idx
        else:
            self.state = self.STATE_DONE
            self.shown_before = False
            self.input_idx = 0

    def export(self, session):
        """Export the session state."""
        return dict(session, **{
            "lang": self.lang,
            "state": self.state,
            "shown_before": self.shown_before,
            "input_idx": self.input_idx,
            "instance": self.instance.to_dict(),
            })

    def choose(self, response, choices):
        """Return a choice from a list of strings.

        Return None if the choise is invalid.
        """
        if not response.isdigit():
            return None
        i = int(response) - 1
        if i < 0 or i >= len(choices):
            return None
        return choices[i]

    def interact_new(self, response):
        languages = self.xform.model.itext.languages()
        if self.shown_before:
            choice = self.choose(response, languages)
            if choice is not None:
                self.lang = choice
                self.set_question(0)
                return self.interact(None)
            else:
                lines = ["Invalid language. Please select a language:"]
        else:
            lines = [self.xform.title, "Please select a language:"]

        for i, lang in enumerate(languages):
            lines.append("%d. %s" % (i + 1, lang))

        self.shown_before = True
        return "\n".join(lines), True

    def interact_question(self, response):
        xinput = self.xform.get_inputs(self.instance)[self.input_idx]
        translator = self.xform.model.itext.translator(self.lang)
        renderer = SimpleTextRenderer(translator)
        if self.shown_before:
            response = renderer.parse(xinput, response)
            self.xform.model.process_input(self.instance, xinput.ref, response)
            self.set_question(self.input_idx + 1)
            return self.interact(None)
        self.shown_before = True
        return renderer.render(xinput), True

    def interact_done(self, msg):
        self.shown_before = True
        return "Survey complete. Goodbye.", False

    def interact(self, msg):
        """Return reply and whether session is concluded."""
        response = msg.strip() if msg else msg
        handler = getattr(self, "interact_%s" % self.state)
        return handler(response)


class SingleFormWorker(ApplicationWorker):

    MAX_SESSION_LENGTH = 3 * 60

    @inlineCallbacks
    def startWorker(self):
        with open(self.config["xform"], "rb") as xform_file:
            self.xform = OdkForm(xform_file)

        self.session_manager = yield SessionManager.from_redis_config(
            self.config.get('redis_manager'),
            "%(worker_name)s:%(transport_name)s" % self.config,
            max_session_length=self.MAX_SESSION_LENGTH)

        yield super(SingleFormWorker, self).startWorker()

    def stopWorker(self):
        return self.session_manager.stop()

    @inlineCallbacks
    def load_or_create_session(self, user_id):
        session = yield self.session_manager.load_session(user_id)
        if not session:
            session = yield self.session_manager.create_session(user_id)
        returnValue(dict((k, json.loads(v)) for k, v in session.items()))

    def save_session(self, user_id, session):
        return self.session_manager.save_session(user_id, dict(
                (k, json.dumps(v)) for k, v in session.items()))

    @inlineCallbacks
    def consume_user_message(self, msg):
        user_id = msg.user()
        session = yield self.load_or_create_session(user_id)
        handler = FormHandler(user_id, self.xform, session)
        reply, continue_session = handler.interact(msg['content'])
        yield self.save_session(user_id, handler.export(session))
        yield self.reply_to(msg, reply, continue_session=continue_session)
