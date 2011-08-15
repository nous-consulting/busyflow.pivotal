# -*- encoding: utf-8 -*-
import unittest2
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
