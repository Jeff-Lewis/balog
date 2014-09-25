from __future__ import unicode_literals
import unittest

from balog.consumers import ConsumerHub
from ..fixtures import my_consumers


class TestConsumer(unittest.TestCase):

    def test_consumer_hub(self):
        hub = ConsumerHub()
        hub.scan(my_consumers)

        self.assertEqual(len(hub.consumers), 2)
        funcs = set(consumer.func for consumer in hub.consumers)
        self.assertEqual(
            funcs,
            set([my_consumers.consumer_a, my_consumers.consumer_b]),
        )
