from __future__ import unicode_literals
import unittest

import mock

from balog import consumers, engines

from tests import fixtures


class TestSQSEngine(unittest.TestCase):

    def setUp(self):
        self.hub = consumers.ConsumerHub()
        self.hub.scan(fixtures.my_consumers)
        self.region = 'us-east-1'
        self.access_key_id = 'AK123'
        self.aws_secret_access_key = 'secret'
        self.engine = engines.SQSEngine(
            self.hub, self.region, self.access_key_id,
            self.aws_secret_access_key
        )
        self.engine.conn = self.conn = mock.Mock()

    def test_messages(self):
        queue, messages = self.engine.messages('topic')
        self.assertEqual(queue, self.conn.get_queue())
        self.assertEqual(messages, self.conn.get_queue().get_messages())

    def test_on_message(self):
        queue, message = self.engine.messages('topic')
        message.get_body.return_value = fixtures.load_text('message.json')
        consumers = []
        self.engine.on_message((queue, message), consumers)
        args, _ = queue.delete_message.call_args
        self.assertTrue(args[0], message)
