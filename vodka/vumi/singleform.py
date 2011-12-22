# -*- test-case-name: vodka.vumi.tests.test_singleform -*-

"""
Vumi ApplicationWorker that serves a single form.
"""

import json

from twisted.internet.defer import inlineCallbacks

from vumi.application import ApplicationWorker, SessionManager
from vumi.utils import get_deploy_int

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
        if "instance" in session:
            data = json.loads(session.get("instance"))
        else:
            data = None
        self.instance = self.xform.model.get_instance(data)

    def set_question(self, input_idx):
        if 0 <= input_idx < len(self.xform.inputs):
            self.state = self.STATE_QUESTION
            self.shown_before = False
            self.input_idx = input_idx
        else:
            self.state = self.STATE_DONE
            self.shown_before = False
            self.input_idx = 0

    def save(self, session, session_manager):
        """Save the session state."""
        session.update({
            "lang": self.lang,
            "state": self.state,
            "shown_before": self.shown_before,
            "input_idx": self.input_idx,
            })
        session_manager.save_session(self.user_id, session)

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
        xinput = self.xform.inputs[self.input_idx]
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

        self.session_manager = SessionManager(
            get_deploy_int(self._amqp_client.vhost),
            "%(worker_name)s:%(transport_name)s" % self.config,
            max_session_length=self.MAX_SESSION_LENGTH)

        yield super(SingleFormWorker, self).startWorker()

    def stopWorker(self):
        self.session_manager.stop()

    def load_or_create_session(self, user_id):
        session = self.session_manager.load_session(user_id)
        if not session:
            session = self.session_manager.create_session(user_id)
        return session

    def consume_user_message(self, msg):
        user_id = msg.user()
        session = self.load_or_create_session(user_id)
        handler = FormHandler(user_id, self.xform, session)
        reply, continue_session = handler.interact(msg['content'])
        handler.save(session, self.session_manager)
        self.reply_to(msg, reply, continue_session=continue_session)
