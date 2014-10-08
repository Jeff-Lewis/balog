#!/usr/bin/env python
"""
Example kafka consumer. Run like

./extras/sample_consumer.py kafka 10.4.120.173  10.4.121.41 10.4.122.213

"""
from __future__ import unicode_literals
import argparse
import json
import logging

import balog
import kafka

import sample


bs = {
    "header": {
        "timestamp": "2014-10-07T15:06:51.641083+00:00",
        "id": "LGk37Fo3xLLVx9GrfnyTuvBd",
        "context": {},
        "channel": "tests.unit.test_log.foobar"
    },
    "payload": {
        "cls_type": "metrics",
        "values": [
            {
                "name": "foo",
                "value": "1234.0"
            },
            {
                "name": "bar",
                "value": "5678.0"
            }
        ]
    },
    "schema": "0.0.1"
}


def run_kafka(args):
    client = kafka.KafkaClient(args.server)
    producer = kafka.SimpleProducer(client)

    # invalid message
    producer.send_messages(str('test'), json.dumps({}))

    # 3x valid messages
    for _ in xrange(3):
        producer.send_messages(str('test'), json.dumps(bs))

    hub = balog.consumers.ConsumerHub()
    hub.scan(sample)
    engine = balog.engines.KafkaEngine(
        hub=hub,
        kafka_server=args.server,
        group=args.group,
        topic=args.topic
    )
    engine.run()


if __name__ == '__main__':
    common = argparse.ArgumentParser(add_help=False)
    parents = [common]
    parser = argparse.ArgumentParser(
        parents=parents,
        description='',
    )
    cmds = parser.add_subparsers(title='commands')
    cmd = cmds.add_parser(
        'kafka',
        parents=parents,
        description='kafka consumer',
    )

    cmd.add_argument('server', nargs='+')
    cmd.add_argument('topic')
    cmd.add_argument('group')
    cmd.set_defaults(cmd=run_kafka)
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    args.cmd(args)
