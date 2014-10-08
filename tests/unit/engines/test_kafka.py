from __future__ import unicode_literals
import unittest

import mock

from balog import consumers, engines

from tests import fixtures


class TestKafkaEngine(unittest.TestCase):

    def setUp(self):
        self.hub = consumers.ConsumerHub()
        self.hub.scan(fixtures.my_consumers)
        self.address = '192.168.1.1:9202'
        self.group = 'group'
        self.topic = 'topic'
        self.engine = engines.KafkaEngine(
            self.hub, self.address, self.group, self.topic
        )

    @mock.patch('balog.engines._kafka.kafka')
    def test_defaults(self, kafka):
        self.assertEqual(self.engine.client, kafka.KafkaClient())
        args, _ = kafka.KafkaClient.call_args_list[0]
        self.assertEqual(args[0], self.address)
        self.assertEqual(
            self.engine.consumer(self.topic), kafka.SimpleConsumer()
        )
        args, _ = kafka.SimpleConsumer.call_args_list[0]
        self.assertEqual(
            args, (kafka.KafkaClient(), self.group, self.topic)
        )
        offset_and_message = mock.Mock()
        kafka.SimpleConsumer.return_value = [offset_and_message]
        self.assertEqual(
            list(self.engine.messages(self.topic)),
            [offset_and_message.message.value]
        )
