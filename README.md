balog
=====

[![Build Status](https://travis-ci.org/balanced/balog.svg?branch=master)](https://travis-ci.org/balanced/balog)

Balanced event logging schema and library

Log schema design goals
=======================

 - Schema version annotated
 - Provide sufficient information about the event
 - Open and close (be flexible, avoid unnecessary change to schema)

Design rationals
================

OSI Network Model Structure
---------------------------

Data in the log can be divided into two major groups, one is the meta data,
which is the data about the event. The another group is the log for application 
itself. In most cases, applications should only be interested in the 
application log itself. And the logging facility should only be interested in 
how to handle the whole event rather than to consume the content of application 
log. Also, since schema of application can variant, we don't want change the
whole schema everytime when application log is change. Consider these issues,
one idea come to my mind is Internet OSI model is actually dealing with the
same issue. It's like TCP/IP protocol doesn't need to know the content of
application layer. Similarly, logging facility doesn't have to know the content
of application log. With this idea in mind, I define two layers for our logging
system.

 - Facility layer
 - Application layer

Facility layer is all about the event, when it is generated, who emited this
event, what's its routing tag and etc. Application layer is all about
application data, like a dispute is processed, a debit is created and etc.

Usage
=====

Produce logs
------------

To produce a log, here you can write

```python
from balog import get_logger
balogger = get_logger(__name__)

balogger.info('done', payload={
    'cls_type': 'metrics',
    'values': [
        {'name': 'total', 'value': 123},
        {'name': 'succeeded', 'value': 456},
        {'name': 'failed', 'value': 789},
    ],
})
```

The channel name will be the logger name + the given suffix name, in the above example, the say if the `__name__` is 
`justitia.scripts.process_results` here, then the channel name will be `justitia.scripts.process_results.done`. If you want to overwrite the channel name, you can also pass `channel` argument to balog logging methods.

Consume logs
------------

To consume events, you can use `consumer_config` like this

```python
from balog.consumers import consumer_config

@consumer_config(
    topic='myproj-events-{env}',
    cls_type='metrics',
    version='<1.0',
)
def process_metrics(settings, event):
    pass
```

This `consumer_config` decorator is mainly for declaring what this consumer wants, in the example above, since want to subscribe the queue `myproj-events-develop` or `myproj-events-prod`, so we set the topic to `myproj-events-{env}`, for the `{env}` placeholder, we will talk about that later. And then we're only interested in `metrics` type events, so we set `cls_type` to `metrics`. We also don't want to process events that are not compatible, so we set the `version` to `<1.0`. 

With these configured consumers, to process events, you need to use `ConsumerHub` first. It is basically a collection of consumers. It provides scanning method to make collecting consumers pretty easy. For example, here you can write

```python
import yourpackage
from balog.consumers import ConsumerHub

hub = ConsumerHub()
hub.scan(yourpackage)
```

By doing that, you have all consuemrs in the hub. Then you can create an event processing engine. We only have Amazon SQS event processing engine for now, but it should be fairly easy to impelement any other engine type as they are needed. Before we create the engine, you need to define a `ConsumerOperator` first. It's basically an object which knows how to operate these consumer. So that you can call these consumer functions in the way you want. Here is an example:


```python
class ConsumerOperator(object):

    def __init__(self, settings):
        self.settings = settings

    def get_topic(self, consumer):
        env = self.settings['api.sqs.queue_env']
        return consumer.topic.format(env=env)

    def process_event(self, consumer, event):
        return consumer.func(self.settings, event)
```

It has two methods, the first is `get_topic`, it is for getting topic, namely, the queue name to subscribe. As we saw the topic name in `consumer_config` is `myproj-events-{env}` above, here I explain why it looks like that. Since we may need to subscribe to different event queue in different environment, like integration or production environment, so we cannot just leave a static value there. To make it as flexible as possible, I let the consumer operator decide how to get the topic name. So in our example, you can see it gets `api.sqs.queue_env` from settings and replace the `env` placeholder. By doing that, we can determine which queue to subscribe later. Similar to the deferred topic name, I also want to make it possible to call the consumer function in the way you like, the `process_event` method of consumer operator is for that purpose. Since in our consumer handler function, we may need some extra information other than just the event, in our example, we also need to read settings. So that in our example, we pass an extra argument `settings` to the consumer function.

Okay, now let's put it altogether


```python
from __future__ import unicode_literals

from balog.consumers import ConsumerHub
from balog.consumers.sqs import SQSEngine

import yourpackage


class ConsumerOperator(object):

    def __init__(self, settings):
        self.settings = settings

    def get_topic(self, consumer):
        env = self.settings['api.sqs.queue_env']
        return consumer.topic.format(env=env)

    def process_event(self, consumer, event):
        return consumer.func(self.settings, event)


def process_events(settings):
    """Process log events in SQS

    """
    hub = ConsumerHub()
    hub.scan(yourpackage)
    consumer_op = ConsumerOperator(settings)
    engine = SQSEngine(
        hub=hub,
        region=settings['api.sqs.region'],
        aws_access_key_id=settings['api.sqs.aws_access_key_id'],
        aws_secret_access_key=settings['api.sqs.aws_secret_access_key'],
        consumer_operator=consumer_op,
    )
    engine.run()
```
