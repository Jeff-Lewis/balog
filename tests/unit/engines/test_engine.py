from __future__ import unicode_literals
import unittest

import mock

from balog import consumers, engines

from tests import fixtures


event = {
    'payload': {
        'cls_type': '88'
    }
}


class TestEngine(unittest.TestCase):

    def setUp(self):
        self.hub = consumers.ConsumerHub()
        self.hub.scan(fixtures.my_consumers)
        self.engine = engines.Engine(self.hub)

    def test_defaults(self):
        self.assertFalse(self.engine.running)
        self.assertEqual(type(self.engine.schema), self.engine.schema_cls)
        with self.assertRaises(NotImplementedError):
            self.engine.messages(None)

    def test_filter(self):
        filtered_consumers = list(
            self.engine.filter_consumers(event, self.hub)
        )
        # None and 88
        self.assertEqual(len(filtered_consumers), 3)

    def test_on_event(self):
        with mock.patch.object(
            self.engine.consumer_operator, 'process_event'
        ) as pe:
            self.engine.on_event(event, self.hub)
        self.assertEqual(pe.call_count, 3)

    def test_on_event_default(self):
        with mock.patch.object(
            self.engine, 'default_event_handler'
        ) as de:
            self.engine.on_event(event, [])
        self.assertEqual(de.call_count, 1)

    def test_on_message(self):
        with mock.patch.object(
                self.engine, 'on_event'
        ) as oe:
            self.engine.on_message(
                fixtures.load_text('message.json'),
                None
            )
        self.assertEqual(oe.call_count, 1)

    def test_consumers_by_topic(self):
        consumers_by_topic = self.engine.consumers_by_topic()
        self.assertEqual(
            set(consumers_by_topic.keys()),
            {'5566', 'spam.eggs', 'foo.bar'}
        )
