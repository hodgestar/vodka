"""Tests for vodka.vumi.singleform."""

from unittest import TestCase as UnittestTestCase
from pkg_resources import resource_stream, resource_filename

from twisted.internet.defer import inlineCallbacks

from vumi.tests.utils import FakeRedis, get_stubbed_worker
from vumi.application import SessionManager
from vumi.application.tests.test_base import ApplicationTestCase

from vodka.vumi.singleform import FormHandler, SingleFormWorker
from vodka.xforms import OdkForm


class TestFormHandler(UnittestTestCase):
    def setUp(self):
        self.sm = SessionManager(db=0, prefix="test")
        self.sm.r_server = FakeRedis()  # setup fake redis
        self.xform = OdkForm(resource_stream("vodka.tests",
                                             "example-form.xml"))

    def tearDown(self):
        self.sm.stop()
        self.sm.r_server.teardown()  # teardown fake redis

    def mk_handler(self, user_id, session):
        return FormHandler(user_id, self.xform, session)

    def test_interact_new(self):
        handler = self.mk_handler("user1", {})
        reply, continue_session = handler.interact(None)
        self.assertEqual(reply, "Example Vodka Form\n"
                         "Please select a language:\n"
                         "1. eng")
        self.assertTrue(continue_session)
        self.assertEqual(handler.state, handler.STATE_NEW)
        self.assertEqual(handler.shown_before, True)

    def test_select_lang(self):
        handler = self.mk_handler("user1", {"shown_before": True})
        reply, continue_session = handler.interact("1")
        self.assertEqual(reply, "Enter your full name")
        self.assertTrue(continue_session)
        self.assertEqual(handler.state, handler.STATE_QUESTION)
        self.assertEqual(handler.shown_before, True)
        self.assertEqual(handler.input_idx, 0)

    def test_fail_to_select_lang(self):
        handler = self.mk_handler("user1", {"shown_before": True})
        reply, continue_session = handler.interact("2")
        self.assertEqual(reply, "Invalid language. Please select a language:\n"
                         "1. eng")
        self.assertTrue(continue_session)
        self.assertEqual(handler.state, handler.STATE_NEW)
        self.assertEqual(handler.shown_before, True)

    def test_answer_question(self):
        handler = self.mk_handler("user1", {
            "state": FormHandler.STATE_QUESTION,
            "lang": "eng",
            "input_idx": 0,
            "shown_before": True,
            })
        reply, continue_session = handler.interact("George Vollenaam")
        self.assertEqual(reply, "Enter your phone number")
        self.assertTrue(continue_session)
        self.assertEqual(handler.state, handler.STATE_QUESTION)
        self.assertEqual(handler.shown_before, True)
        self.assertEqual(handler.input_idx, 1)

    def test_answer_last_question(self):
        handler = self.mk_handler("user1", {
            "state": FormHandler.STATE_QUESTION,
            "lang": "eng",
            "input_idx": 2,
            "shown_before": True,
            })
        reply, continue_session = handler.interact("2")
        self.assertEqual(reply, "Survey complete. Goodbye.")
        self.assertFalse(continue_session)
        self.assertEqual(handler.state, handler.STATE_DONE)
        self.assertEqual(handler.shown_before, True)
        self.assertEqual(handler.input_idx, 0)

    def test_save(self):

        class DummyManager(object):
            saves = {}

            def save_session(self, user_id, session):
                self.saves[user_id] = session

        handler = self.mk_handler("user1", {
            "state": FormHandler.STATE_QUESTION,
            "lang": "eng",
            "input_idx": 2,
            "shown_before": True,
            })
        handler.save({"created_at": "123"}, DummyManager())

        self.assertEqual(DummyManager.saves, {
            "user1": {
                "created_at": "123",
                "state": FormHandler.STATE_QUESTION,
                "lang": "eng",
                "input_idx": 2,
                "shown_before": True,
                },
            })


class TestSingleFormWorker(ApplicationTestCase):

    timeout = 3
    application_class = SingleFormWorker

    @inlineCallbacks
    def setUp(self):
        super(TestSingleFormWorker, self).setUp()
        self.worker = yield self.get_application({
                'worker_name': 'test_singleform',
                'xform': resource_filename("vodka.tests",
                                           "example-form.xml"),
                })
        self.worker.session_manager.r_server = FakeRedis()  # stub out redis

    def tearDown(self):
        super(TestSingleFormWorker, self).tearDown()
        self.worker.session_manager.r_server.teardown()  # teardown fake redis

    @inlineCallbacks
    def test_consume_and_create_session(self):
        msg = self.mkmsg_in(from_addr="+1234", content="hi?")
        yield self.dispatch(msg)

        [reply] = self.get_dispatched_messages()
        self.assertEqual(reply["content"],
                         "Example Vodka Form\n"
                         "Please select a language:\n"
                         "1. eng")
        self.assertEqual(reply["session_event"], None)

        session = self.worker.session_manager.load_session("+1234")
        session.pop("created_at")
        self.assertEqual(session, {
            "lang": None,
            "input_idx": 0,
            "state": FormHandler.STATE_NEW,
            "shown_before": True,
            })

    @inlineCallbacks
    def test_consume_with_existing_session(self):
        self.worker.session_manager.save_session("+1234", {
            "created_at": 123,
            # give input_idx non-default value so we can be
            # sure its been overridden
            "input_idx": 1,
            "state": FormHandler.STATE_NEW,
            "shown_before": True,
            })
        msg = self.mkmsg_in(from_addr="+1234", content="1")
        yield self.dispatch(msg)

        [reply] = self.get_dispatched_messages()
        self.assertEqual(reply["content"], "Enter your full name")
        self.assertEqual(reply["session_event"], None)

        session = self.worker.session_manager.load_session("+1234")
        self.assertEqual(session, {
            "created_at": 123,
            "lang": "eng",
            "input_idx": 0,
            "state": FormHandler.STATE_QUESTION,
            "shown_before": True,
            })
