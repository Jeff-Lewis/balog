from __future__ import unicode_literals

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
        scanner.add_consumer(ob, *args, **kwargs)

    def decorator(wrapped):
        venusian.attach(wrapped, callback, category='balog.consumers')
        return wrapped

    return decorator


class Consumer(object):
    """A consumer represents a function with certain configurations for
    consuming events

    """

    def __init__(self, func, topic, cls_types=None):
        self.func = func
        self.topic = topic
        self.cls_types = cls_types


class ConsumerHub(object):
    """Consumer hub is a collection of consumers, you can feed it with events,
    and it knows which consumers to route those events to

    """

    def __init__(self):
        self.consumers = []

    def add_consumer(self, func, topic, cls_types=None):
        """Add a function as a consumer

        """
        self.consumers.append(Consumer(
            func=func,
            topic=topic,
            cls_types=cls_types,
        ))

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
        # TODO:

    def process(self, events):
        """Process events

        """
        # TODO:
