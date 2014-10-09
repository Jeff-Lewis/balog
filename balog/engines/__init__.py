from __future__ import unicode_literals
import collections
import functools
import json
import logging
import threading

import time

from balog.consumers import DefaultConsumerOperator
from balog.records.facility import FacilityRecordSchema


logger = logging.getLogger(__name__)


class Engine(object):

    _default_consumer_operator = DefaultConsumerOperator

    schema_cls = FacilityRecordSchema

    def __init__(self, hub, consumer_operator=None, default_event_handler=None):
        self.hub = hub
        self.consumer_operator = (
            consumer_operator or self._default_consumer_operator
        )
        self.default_event_handler = default_event_handler
        self.running = False

    @property
    def schema(self):
        return self.schema_cls()

    def filter_consumers(self, event, consumers):
        for consumer in consumers:
            if consumer.match_event(event):
                yield consumer

    def on_event(self, event, consumers):
        # Notice: Since we're processing logs, if we generate
        # log and that will be consumed by this loop, it may
        # end up with flood issue (one log generates more logs)
        # so, we should be careful, do not generate log record
        # from this script
        logger.debug('Processing event %r', event)
        matching_consumers = self.filter_consumers(event, consumers)
        processed = False
        for consumer in matching_consumers:
            self.consumer_operator.process_event(consumer, event)
            processed = True
        if not processed and self.default_event_handler:
            self.default_event_handler(event)

    def on_deserialization_error(self, raw_message, error):
        logger.error(
            'Failed to parse "%s": %r (%s)', raw_message, error, error
        )

    def on_error(self, event, error):
        logger.error(
            'Error handling "%s": %r (%s)', event, error, error
        )

    def on_message(self, message, consumers):
        json_data = json.loads(message)
        try:
            event = self.schema.deserialize(json_data)
        except Exception as ex:
            self.on_deserialization_error(message, ex)
        else:
            try:
                self.on_event(event, consumers)
            except Exception as ex:
                self.on_error(event, ex)

    def messages(self, topic):
        raise NotImplementedError()

    def poll_topic(self, topic, consumers):
        logger.info(
            'Polling %s for consumers %s',
            topic, consumers,
        )
        while self.running:
            for message in self.messages(topic):
                self.on_message(message, consumers)
                if not self.running:
                    break

    def consumers_by_topic(self):
        # map topic name (queue name) to consumers
        topic_to_consumers = collections.defaultdict(list)
        for consumer in self.hub.consumers:
            topic = self.consumer_operator.get_topic(consumer)
            topic_to_consumers[topic].append(consumer)
        return topic_to_consumers

    def run(self):
        # create threads for consuming events from datastore
        self.running = True
        consumers = self.consumers_by_topic()
        threads = []
        for topic, consumers in consumers.iteritems():
            thread = threading.Thread(
                target=functools.partial(self.poll_topic, topic, consumers),
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
            logger.info('Stopping %s', self.__class__.__name__)

        for thread in threads:
            thread.join(timeout=10.0)

        logger.info('Stopped %s', self.__class__.__name__)


from _kafka import KafkaEngine
from sqs import SQSEngine
