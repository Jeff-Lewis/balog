from __future__ import unicode_literals
import collections
from distutils.version import StrictVersion
import functools
import json
import logging
import threading

import venusian
import time

from balog.records.facility import FacilityRecordSchema


logger = logging.getLogger(__name__)


def consumer_config(*args, **kwargs):
    """Decorator for configure the given consumer function. For example,
    you want to consume a certain type of events from the queue, here you can
    write

        @consumer_config(
            topic='justitia.generic_events',
            cls_type=('metrics', ),
        )
        def process_metrics(event):
            '''Process metrics events and push values to librato

            '''
            # the code goes here

    """
    def callback(scanner, name, ob):
        consumer_cls = kwargs.pop('consumer_cls', Consumer)
        if 'name' not in kwargs:
            kwargs['name'] = name
        consumer = consumer_cls(ob, *args, **kwargs)
        scanner.add_consumer(consumer)

    def decorator(wrapped):
        venusian.attach(wrapped, callback, category='balog.consumers')
        return wrapped

    return decorator


def _to_tuple(obj):
    if obj is not None and not isinstance(obj, tuple):
        return (obj, )
    return obj


class Consumer(object):
    """A consumer represents a function with certain configurations for
    consuming events

    """

    VERSION_OPS = {
        '<': lambda lhs, rhs: lhs < rhs,
        '<=': lambda lhs, rhs: lhs <= rhs,
        '>': lambda lhs, rhs: lhs > rhs,
        '>=': lambda lhs, rhs: lhs >= rhs,
        '==': lambda lhs, rhs: lhs == rhs,
    }

    def __init__(self, func, topic, cls_type=None, version=None, name=None):
        self.func = func
        self.topic = topic
        #: predicate that limits cls_type of event
        self.cls_type = _to_tuple(cls_type)
        #: predicate that limits schema version number
        self.version = _to_tuple(version)
        self.name = name

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            self.name or self.func,
        )

    def _parse_version_condition(self, version_condition):
        """Parse given version_condition, and return a function that returns
        a boolean value which indicates whether the given schema version meets
        the condition

        """
        for op_symbol, condition_op in self.VERSION_OPS.iteritems():
            if version_condition.startswith(op_symbol):
                break
        else:
            raise ValueError(
                'Bad version condition, should start with either '
                '>, >=, <, <= or ==, then the version numbers, e.g. '
                '>=1.0.1'
            )

        # the version number part in version condition, e.g 1.0.0
        rhs_operant = version_condition[len(op_symbol):]

        # version number compare recipe from
        # http://stackoverflow.com/questions/1714027/version-number-comparison
        def op_func(schema_version):
            return condition_op(
                StrictVersion(schema_version),
                StrictVersion(rhs_operant),
            )

        return op_func

    def match_event(self, event):
        """Return whether is this consumer interested in the given event

        """
        if (
            self.cls_type and event['payload']['cls_type'] not in self.cls_type
        ):
            return False
        if self.version:
            schema_version = event['schema']
            for version_condition in self.version:
                op_func = self._parse_version_condition(version_condition)
                if not op_func(schema_version):
                    return False
        return True


class ConsumerHub(object):
    """Consumer hub is a collection of consumers, you can feed it with events,
    and it knows which consumers to route those events to

    """

    def __init__(self):
        self.consumers = []

    def add_consumer(self, consumer):
        """Add a function as a consumer

        """
        self.consumers.append(consumer)

    def scan(self, package, ignore=None):
        """Scan packages for finding consumers

        """
        scanner = venusian.Scanner(add_consumer=self.add_consumer)
        scanner.scan(
            package,
            categories=('balog.consumers', ),
            ignore=ignore,
        )

    def route(self, event):
        """Return a list of consumers for the given event should be routed to

        """
        for consumer in self.consumers:
            if not consumer.match_event(event):
                continue
            yield consumer

    def __iter__(self):
        for consumer in self.consumers:
            yield consumer


class DefaultConsumerOperator(object):

    @classmethod
    def get_topic(cls, consumer):
        """Get the topic of consumer

        """
        return consumer.topic

    @classmethod
    def process_event(cls, consumer, event):
        """Call consumer's function

        """
        return consumer.func(event)


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

    def on_message(self, message, consumers):
        json_data = json.loads(message)
        event = self.schema.deserialize(json_data)
        self.on_event(event, consumers)

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
            thread.join()

        logger.info('Stopped %s', self.__class__.__name__)
