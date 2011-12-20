"""Test for vodka.xtypes."""

from unittest import TestCase

from vodka.xtypes import StringType, IntType, Select1Type


class TestStringType(TestCase):

    def test_valid(self):
        string_type = StringType()
        string_type.set_value("foo")
        self.assertEqual("foo", string_type.get_value())


class TestIntType(TestCase):

    def test_valid(self):
        int_type = IntType()
        int_type.set_value("1")
        self.assertEqual(1, int_type.get_value())


class TestSelect1Type(TestCase):

    def test_valid(self):
        select1_type = Select1Type({
                'items': ['foo', 'bar', 'baz'],
                })
        select1_type.set_value("foo")
        self.assertEqual("foo", select1_type.get_value())
