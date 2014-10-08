from __future__ import unicode_literals
import logging
import time

import kafka

from . import Engine

# Notice: this logger should be configured carefully
logger = logging.getLogger(__name__)


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

    def consumer(self, topic):
        try:
            return kafka.SimpleConsumer(self.client, self.group, str(topic))
        except KeyError:
            # topic does not exist, hack in a back off period
            time.sleep(5)
            return []

    def messages(self, topic):
        for offset_and_message in self.consumer(topic):
            yield offset_and_message.message.value

    def run(self):
        super(KafkaEngine, self).run()
        try:
            self.client.close()
        except:
            pass
