# -*- encoding: utf-8 -*-
import unittest2
import datetime
from textwrap import dedent

from busyflow.pivotal import PivotalClient


class TestPivotalClient(unittest2.TestCase):

    def test_make_story_xml(self):
        client = PivotalClient('')
        result = client.stories.make_story_xml('Some story', 'Do some stuff', 'feature',
                                               requested_by=u'Ignas Mikalajūnas')
        expected = """
        <story>
            <name>Some story</name>
            <description>Do some stuff</description>
            <requested_by>Ignas Mikalajūnas</requested_by>
            <story_type>feature</story_type>
        </story>"""
        self.assertEqual(result, dedent(expected).strip())

        result = client.stories.make_story_xml('Some story', 'Do some stuff', 'feature',
                                               requested_by=u'Ignas Mikalajūnas',
                                               estimate=3,
                                               current_state='started',
                                               labels=['l1', 'l2'])
        expected = """
        <story>
            <name>Some story</name>
            <description>Do some stuff</description>
            <requested_by>Ignas Mikalajūnas</requested_by>
            <story_type>feature</story_type>
            <estimate type="integer">3</estimate>
            <current_state>started</current_state>
            <labels>l1,l2</labels>
        </story>"""
        self.assertEqual(result, dedent(expected).strip())


        result = client.stories.make_story_xml('Some story', 'Do some stuff', 'feature',
                                               requested_by=u'Ignas Mikalajūnas',
                                               estimate=3,
                                               current_state='started',
                                               labels=[])
        expected = """
        <story>
            <name>Some story</name>
            <description>Do some stuff</description>
            <requested_by>Ignas Mikalajūnas</requested_by>
            <story_type>feature</story_type>
            <estimate type="integer">3</estimate>
            <current_state>started</current_state>
            <labels>,</labels>
        </story>"""
        self.assertEqual(result, dedent(expected).strip())


    def test_parse_story_xml(self):
        client = PivotalClient('')
        story_xml = """
          <story>
            <id type="integer">123</id>
            <project_id type="integer">456</project_id>
            <story_type>feature</story_type>
            <url>http://www.pivotaltracker.com/story/show/123</url>
            <estimate type="integer">1</estimate>
            <current_state>accepted</current_state>
            <description></description>
            <name>Purchase Order</name>
            <requested_by>Anon</requested_by>
            <owned_by>Anon</owned_by>
            <created_at type="datetime">2012/01/01 11:00:00 UTC</created_at>
            <updated_at type="datetime">2012/01/01 11:00:00 EST</updated_at>
            <accepted_at type="datetime">2012/01/01 11:00:00 EEST</accepted_at>
          </story>
        """
        story = client.parseContent(story_xml)
        self.assertEqual(
            story,
            {u'story': {u'current_state': u'accepted',
                        u'description': '',
                        u'estimate': 1,
                        u'id': 123,
                        u'name': u'Purchase Order',
                        u'owned_by': u'Anon',
                        u'project_id': 456,
                        u'requested_by': u'Anon',
                        u'story_type': u'feature',
                        u'created_at': datetime.datetime(2012, 1, 1, 11, 0),
                        u'updated_at': datetime.datetime(2012, 1, 1, 6, 0),
                        u'accepted_at': datetime.datetime(2012, 1, 1, 14, 0),
                        u'url': u'http://www.pivotaltracker.com/story/show/123'}})

