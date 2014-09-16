from __future__ import unicode_literals
import unittest
import logging
import json

from balog import configure
from balog import get_logger


class DummyHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super(DummyHandler, self).__init__(*args, **kwargs)
        self.records = []

    def emit(self, record):
        self.records.append(record)


class TestLog(unittest.TestCase):

    def test_log(self):
        handler = DummyHandler()
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        configure()
        logger = get_logger()
        logger.info('foobar', payload={
            'cls_type': 'metrics',
            'values': [
                {'name': 'foo', 'value': 1234},
                {'name': 'bar', 'value': 5678},
            ]
        })
        self.assertEqual(len(handler.records), 1)
        msg = handler.records[0].getMessage()
        log_dict = json.loads(msg)
        self.assertEqual(log_dict['schema'], '0.0.1')
        self.assertTrue(log_dict['header']['id'].startswith('LG'))
        self.assertEqual(log_dict['header']['channel'],
                         'tests.unit.test_log.foobar')
        self.assertEqual(log_dict['payload'], {
            'cls_type': 'metrics',
            'values': [
                {'name': 'foo', 'value': '1234.0'},
                {'name': 'bar', 'value': '5678.0'},
            ]
        })
