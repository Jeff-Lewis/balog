from __future__ import unicode_literals
import logging

import boto.sqs
from boto.sqs.message import RawMessage

from . import Engine

# Notice: this logger should be configured carefully
logger = logging.getLogger(__name__)


# TODO: define a base class?
class SQSEngine(Engine):
    """Event processing engine for polling Amazon SQS queues

    """

    def __init__(
        self,
        hub,
        region,
        aws_access_key_id,
        aws_secret_access_key,
        polling_period=1,
        num_messages=10,
        consumer_operator=None,
        default_event_handler=None,
    ):
        super(SQSEngine, self).__init__(
            hub, consumer_operator, default_event_handler
        )
        # aws credentials
        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        #: polling period in seconds
        self.polling_period = polling_period
        #: maximum number of messages to get at once
        self.num_messages = num_messages
        self.conn = None

    def messages(self, topic):
        queue = self.conn.get_queue(topic)
        queue.set_message_class(RawMessage)
        return queue, queue.get_messages(
            num_messages=self.num_messages,
            wait_time_seconds=self.polling_period,
        )

    def on_message(self, message, consumers):
        queue, message = message
        super(SQSEngine, self).on_message(message.get_body(), consumers)
        queue.delete_message(message)

    def run(self):
        self.conn = boto.sqs.connect_to_region(
            self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        super(SQSEngine, self).run()
