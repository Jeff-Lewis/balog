from __future__ import unicode_literals
from distutils.version import StrictVersion

import venusian


def consumer_config(*args, **kwargs):
    """Decorator for configure the given consumer function. For example,
    you want to consume a certain type of events from the queue, here you can
    write

        @consumer_config(
            topic='justitia.generic_events',
            cls_types=('metrics', ),
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

    def __init__(self, func, topic, cls_types=None, version=None, name=None):
        self.func = func
        self.topic = topic
        #: predicate that limits cls_types of event
        self.cls_types = _to_tuple(cls_types)
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
            self.cls_types is not None and
            event['payload']['cls_type'] not in self.cls_types
        ):
            return False
        if (self.version is not None):
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
