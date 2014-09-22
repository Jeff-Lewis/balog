from __future__ import unicode_literals
import unittest
import logging
import json

from balog import configure
from balog import get_logger
from balog.formatters import SchemaFormatter


class DummyHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super(DummyHandler, self).__init__(*args, **kwargs)
        self.records = []
        self.msgs = []

    def emit(self, record):
        self.records.append(record)
        msg = self.format(record)
        self.msgs.append(msg)


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

    def test_formatter(self):
        formatter = SchemaFormatter()
        handler = DummyHandler()
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        root_logger.info('Hello world')

        self.assertEqual(len(handler.msgs), 1)
        msg = handler.msgs[0]
        log_dict = json.loads(msg)
        self.assertEqual(log_dict['schema'], '0.0.1')
        self.assertTrue(log_dict['header']['id'].startswith('LG'))
        self.assertEqual(log_dict['header']['channel'], 'root')
        self.assertEqual(log_dict['payload'], {
            'cls_type': 'log',
            'message': 'Hello world',
            'severity': 'info',
        })

        # test different severity
        for method_name, severity in [
            ('debug', 'debug'),
            ('info', 'info'),
            ('warn', 'warning'),
            ('error', 'error'),
            ('fatal', 'critical'),
        ]:
            method = getattr(root_logger, method_name)
            method('foobar')
            msg = handler.msgs[-1]
            log_dict = json.loads(msg)
            self.assertEqual(log_dict['payload']['severity'], severity)

    def test_formatter_with_exc(self):
        formatter = SchemaFormatter()
        handler = DummyHandler()
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        try:
            raise ValueError('test')
        except ValueError:
            root_logger.error('test exec', exc_info=True)

        self.assertEqual(len(handler.msgs), 1)
        msg = handler.msgs[0]
        log_dict = json.loads(msg)

        self.assertIn('exc_text', log_dict['payload'])
        self.assertIn('ValueError', log_dict['payload']['exc_text'])
