from __future__ import unicode_literals
import unittest

from balog.consumers import ConsumerHub
from balog.consumers import Consumer
from ..fixtures import my_consumers


class TestConsumer(unittest.TestCase):

    def test_consumer_hub(self):
        hub = ConsumerHub()
        hub.scan(my_consumers)

        self.assertEqual(len(hub.consumers), 3)
        func_to_consumers = dict(
            (consumer.func, consumer)
            for consumer in hub.consumers
        )
        self.assertEqual(
            set(func_to_consumers.keys()),
            set(
                [
                    my_consumers.consumer_a,
                    my_consumers.consumer_b,
                    my_consumers.consumer_c
                ]
            )
        )

        consumer_a = func_to_consumers[my_consumers.consumer_a]
        self.assertEqual(consumer_a.topic, 'foo.bar')
        self.assertEqual(consumer_a.cls_types, ('eggs', ))

        consumer_b = func_to_consumers[my_consumers.consumer_b]
        self.assertEqual(consumer_b.topic, 'spam.eggs')
        self.assertEqual(consumer_b.cls_types, None)

        consumer_c = func_to_consumers[my_consumers.consumer_c]
        self.assertEqual(consumer_c.topic, '5566')
        self.assertEqual(consumer_c.cls_types, ('55', '66'))

        eggs_event = dict(payload=dict(cls_type='eggs'))
        self.assertEqual(
            set(hub.route(eggs_event)),
            set([consumer_a, consumer_b]),
        )

    def test_cls_type_predicate(self):
        pass

    def test_versions_predicate(self):
        consumer_a = Consumer(
            lambda: None,
            'foobar',
            version='>=1.0.1',
        )

        def assert_match(schema_version, consumer):
            self.assertTrue(consumer.match_event(dict(schema=schema_version)))

        def assert_not_match(schema_version, consumer):
            self.assertFalse(consumer.match_event(dict(schema=schema_version)))

        assert_match('1.0.1', consumer_a)
        assert_match('1.0.2', consumer_a)
        assert_match('2.0', consumer_a)
        assert_match('2.0.1', consumer_a)
        assert_not_match('1.0', consumer_a)
        assert_not_match('1.0.0', consumer_a)
        assert_not_match('0.0.9', consumer_a)

        consumer_b = Consumer(
            lambda: None,
            'foobar',
            version=('>=1.0.1', '<2.0'),
        )
        assert_match('1.0.1', consumer_b)
        assert_match('1.0.2', consumer_b)
        assert_match('1.999999', consumer_b)
        assert_match('1.0.9999', consumer_b)
        assert_not_match('1.0', consumer_b)
        assert_not_match('1.0.0', consumer_b)
        assert_not_match('2.0', consumer_b)
        assert_not_match('2.0.0', consumer_b)
        assert_not_match('2.0.1', consumer_b)

        consumer_c = Consumer(
            lambda: None,
            'foobar',
            version='>=1.0.1000',
        )
        assert_match('1.0.1001', consumer_b)
        assert_match('1.0.2002', consumer_b)
        assert_not_match('1.0.999', consumer_c)
        assert_not_match('1.0.1', consumer_c)
