from __future__ import unicode_literals
import unittest

import colander

from balog.records import base
from tests import fixtures


class One(base.PayloadSchema):
    cls_type = 'one'


class Two(base.PayloadSchema):
    cls_type = 'two'
    message = colander.SchemaNode(colander.String())


class Three(Two):
    cls_type = 'three'


class TestLog(unittest.TestCase):

    def setUp(self):
        self.one = fixtures.load_json('one.json')
        self.two = fixtures.load_json('two.json')
        self.three = fixtures.load_json('three.json')

    def test_log(self):
        for fix in (self.one, self.two, self.three):
            result = base.RecordSchema().bind().deserialize(fix)
