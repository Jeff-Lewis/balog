from __future__ import unicode_literals
import logging

import colander

from .. import base

logger = logging.getLogger(__name__)


class Null(base.PayloadSchema):
    cls_type = 'null'


class Log(base.PayloadSchema):
    cls_type = 'log'
    message = colander.SchemaNode(colander.String())
    severity = colander.SchemaNode(colander.String(), validators=[
        colander.OneOf((
            'debug',
            'info',
            'warning',
            'error',
            'critical',
        ))
    ])
    exc_text = colander.SchemaNode(colander.String(), default=colander.drop)


class MetricsValue(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    value = colander.SchemaNode(colander.Float())


class MetricsValues(colander.SequenceSchema):
    value = MetricsValue()


class Metrics(base.PayloadSchema):
    cls_type = 'metrics'
    values = MetricsValues()
