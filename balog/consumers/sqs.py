from __future__ import unicode_literals
import json
import collections
import functools
import threading
import logging
import time

import boto.sqs
from boto.sqs.message import RawMessage

from ..records.facility import FacilityRecordSchema

# Notice: this logger should be configured carefully
logger = logging.getLogger(__name__)


class DefaultConsumerOperator(object):

    def get_topic(self, consumer):
        """Get the topic of consumer

        """
        return consumer.topic

    def process_event(self, consumer, event):
        """Call consumer's function

        """
        return consumer.func(event)


# TODO: define a base class?
class SQSEngine(object):
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
        self.hub = hub
        # aws credentials
        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        #: polling period in seconds
        self.polling_period = polling_period
        #: maximum number of messages to get at once
        self.num_messages = num_messages
        #: the object which knows how to operate consumers
        self.consumer_operator = consumer_operator
        if self.consumer_operator is None:
            self.consumer_operator = DefaultConsumerOperator
        self.default_event_handler = default_event_handler

        self.running = False

    def _poll_topic(self, topic, consumers):
        """Poll events from SQS

        """
        logger.info(
            'Polling %s for consumers %s',
            topic, consumers,
        )
        schema = FacilityRecordSchema()
        queue = self.conn.get_queue(topic)
        queue.set_message_class(RawMessage)
        while self.running:
            msgs = queue.get_messages(
                num_messages=self.num_messages,
                wait_time_seconds=self.polling_period,
            )
            for msg in msgs:
                json_data = json.loads(msg.get_body())
                event = schema.deserialize(json_data)
                # Notice: Since we're processing logs, if we generate
                # log and that will be consumed by this loop, it may
                # end up with flood issue (one log generates more logs)
                # so, we should be careful, do not generate log record
                # from this script
                logger.debug('Processing event %r', event)
                processed = False
                for consumer in consumers:
                    if not consumer.match_event(event):
                        continue
                    # TODO: what about process_event raises exceptions?
                    self.consumer_operator.process_event(consumer, event)
                    processed = True
                # nobody processed this event, let default event handler
                # handle it
                if not processed and self.default_event_handler is not None:
                    self.default_event_handler(event)
                # delete it from queue
                queue.delete_message(msg)

    def run(self):
        self.running = True
        self.conn = boto.sqs.connect_to_region(
            self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        # map topic name (queue name) to consumers
        topic_to_consumers = collections.defaultdict(list)
        for consumer in self.hub.consumers:
            topic = self.consumer_operator.get_topic(consumer)
            topic_to_consumers[topic].append(consumer)

        # create threads for consuming events from SQS
        threads = []
        for topic, consumers in topic_to_consumers.iteritems():
            thread = threading.Thread(
                target=functools.partial(self._poll_topic, topic, consumers),
                name='polling-topic-{}-worker'.format(topic)
            )
            thread.daemon = True
            threads.append(thread)

        # start all threads
        for thread in threads:
            thread.start()

        try:
            while self.running:
                time.sleep(1)
        except (SystemExit, KeyboardInterrupt):
            self.running = False
            logger.info('Stopping SQS engine')

        for thread in threads:
            thread.join()
        logger.info('Stopped SQS engine')
