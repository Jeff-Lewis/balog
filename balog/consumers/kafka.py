from __future__ import unicode_literals
import logging

import kafka

from balog.consumers import Engine

# Notice: this logger should be configured carefully
logger = logging.getLogger(__name__)


# TODO: define a base class?
class KafkaEngine(Engine):
    """Event processing engine for Apache Kafka

    """

    def __init__(
            self,
            hub,
            # like 192.168.1.1:9202
            kafka_server,
            group,
            topic,
            consumer_operator=None,
            default_event_handler=None,
    ):
        super(KafkaEngine, self).__init__(
            hub, consumer_operator, default_event_handler
        )
        # aws credentials
        self.kafka_server = kafka_server
        self.group = group
        self.topic = topic

    @property
    def client(self):
        return kafka.KafkaClient(self.kafka_server)

    @property
    def consumer(self):
        # TODO: looks like consumers can specify many topics
        return kafka.SimpleConsumer(self.client, self.group, self.topic)

    def messages(self, topic):
        return self.consumer

    def poll_topic(self, topic, consumers):
        logger.info(
            'Polling %s for consumers %s',
            topic, consumers,
        )
        while self.running:
            for message in self.consumer:
                self.on_message(message, consumers)
                if not self.running:
                    break

    def run(self):
        super(KafkaEngine, self).run()
        self.client.close()
