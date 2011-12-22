"""Tests for vodka.vumi.singleform."""

from unittest import TestCase
from pkg_resources import resource_stream

from vumi.tests.utils import FakeRedis
from vumi.application import SessionManager

from vodka.vumi.singleform import FormHandler
from vodka.xforms import OdkForm


class TestFormHandler(TestCase):
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
