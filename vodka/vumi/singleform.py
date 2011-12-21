# -*- test-case-name: vodka.vumi.tests.test_singleform -*-

"""
Vumi ApplicationWorker that serves a single form.
"""

from twisted.internet.defer import inlineCallbacks

from vumi.application import ApplicationWorker, SessionManager
from vumi.utils import get_deploy_int

from vodka.xforms import OdkForm
from vodka.renderers import SimpleTextRenderer


class FormHandler(object):
    """Processes user interactions with a form."""

    def __init__(self, user_id, xform, session_manager):
        self.user_id = user_id
        self.xform = xform
        self.session_manager = session_manager
        self.session = self.session_manager.load_session(self.user_id)
        if not self.session:
            self.session = self.session_manager.create_session(self.user_id)

    def save(self):
        """Save the session state."""
        # TODO: this function is only half implemented.
        self.session_manager.save(self.user_id, self.session)

    def interact(self, msg):
        """Return reply and whether session is concluded."""
        # TODO: this function is only half implemented.
        lang = self.session['lang']
        input_index = self.session['input_index']
        input_obj = self.xform.inputs[input_index]
        translator = self.xform.model.itext.translator(lang)
        renderer = SimpleTextRenderer(translator)

        reply = renderer.render(input_obj)
        return reply, True


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

    def consume_user_message(self, msg):
        user_id = msg.user()
        handler = FormHandler(user_id, self.xform, self.session_manager)
        reply, continue_session = handler.interact(msg['content'])
        handler.save()
        self.reply_to(msg, reply, continue_session=continue_session)
