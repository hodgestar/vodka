"""Test for vodka.xmodels."""

from unittest import TestCase

from vodka.methanol import fromstring
from vodka.xmodels import XFormsModel


EXAMPLE1 = """
<model xmlns="http://www.w3.org/2002/xforms">
  <instance>
    <data id="build_Untitled-Form_1323432952">
      <Name>
        Joe Blogs
      </Name>
      <Cell_number/>
      <Favourite_cheese/>
    </data>
  </instance>
  <itext>
    <translation lang="eng">
      <text id="/data/Name:label">
        <value>Enter your full name</value>
      </text>
      <text id="/data/Name:hint">
        <value/>
      </text>
      <text id="/data/Cell_number:label">
        <value>Enter your phone number</value>
      </text>
      <text id="/data/Cell_number:hint">
        <value/>
      </text>
      <text id="/data/Favourite_cheese:label">
        <value>Select your favourite_cheese</value>
      </text>
      <text id="/data/Favourite_cheese:hint">
        <value/>
      </text>
      <text id="/data/Favourite_cheese:option0">
        <value>Gouda</value>
      </text>
      <text id="/data/Favourite_cheese:option1">
        <value>Cheddar</value>
      </text>
    </translation>
  </itext>
  <bind nodeset="/data/Name" type="string" required="true()"/>
  <bind nodeset="/data/Cell_number" type="int"/>
  <bind nodeset="/data/Favourite_cheese" type="select1"/>
</model>
"""

EXAMPLE2 = """
<instance>
  <data id="build_Untitled-Form_1323432952">
    <Name>John Doe</Name>
    <Cell_number/>
    <Favourite_cheese>gouda</Favourite_cheese>
  </data>
</instance>
"""


class TestXFormsModel(TestCase):

    def setUp(self):
        self.model = XFormsModel(fromstring(EXAMPLE1))

    def test_model(self):
        translator = self.model.itext.translator('eng')
        self.assertEqual(translator("jr:itext('/data/Name:label')"),
                         "Enter your full name")
        self.model._process_bindings()

    def test_instance(self):
        instance = self.model.get_instance()
        self.assertEqual('Joe Blogs',
                         instance.find('/data/Name').text.strip())

    def test_elem_path(self):
        instance = self.model.get_instance()
        get_cpath = instance.get_canonical_path
        self.assertEqual('/data/Name', get_cpath('/data/Name'))
        self.assertEqual('/data/Name', get_cpath('/data/Name/'))
        self.assertEqual(None, get_cpath('/data/foo'))

    def test_input_input(self):
        instance = self.model.get_instance()
        self.assertEqual('Joe Blogs',
                         instance.find('/data/Name').text.strip())
        self.assertEqual('Joe Blogs', instance.data['data']['Name'].strip())
        self.model.process_input(instance, '/data/Name', "foo")
        self.assertEqual('foo', instance.find('/data/Name').text.strip())
        self.assertEqual('foo', instance.data['data']['Name'].strip())

    def test_select1_input(self):
        instance = self.model.get_instance()
        self.assertEqual(None, instance.find('/data/Favourite_cheese').text)
        self.assertEqual(None, instance.data['data']['Favourite_cheese'])
        self.model.process_input(instance, '/data/Favourite_cheese', "gouda")
        self.assertEqual('gouda', instance.find('/data/Favourite_cheese').text)
        self.assertEqual('gouda', instance.data['data']['Favourite_cheese'])

    def test_build_instance_from_xml(self):
        instance = self.model.get_instance(EXAMPLE2)
        self.assertEqual('John Doe', instance.find('/data/Name').text)
        self.assertEqual(None, instance.find('/data/Cell_number').text)
        self.assertEqual('gouda', instance.find('/data/Favourite_cheese').text)
        self.assertEqual('John Doe', instance.data['data']['Name'])
        self.assertEqual(None, instance.data['data']['Cell_number'])
        self.assertEqual('gouda', instance.data['data']['Favourite_cheese'])

    def test_build_instance_from_dict(self):
        instance = self.model.get_instance({'data': {
                    'Name': 'John Doe',
                    'Cell_number': None,
                    'Favourite_cheese': 'gouda',
                    }})
        self.assertEqual('John Doe', instance.find('/data/Name').text)
        self.assertEqual(None, instance.find('/data/Cell_number').text)
        self.assertEqual('gouda', instance.find('/data/Favourite_cheese').text)
        self.assertEqual('John Doe', instance.data['data']['Name'])
        self.assertEqual(None, instance.data['data']['Cell_number'])
        self.assertEqual('gouda', instance.data['data']['Favourite_cheese'])
