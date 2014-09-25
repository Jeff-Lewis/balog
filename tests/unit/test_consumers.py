from __future__ import unicode_literals
import unittest

from balog.consumers import ConsumerHub
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
