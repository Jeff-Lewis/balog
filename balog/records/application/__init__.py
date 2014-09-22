from __future__ import unicode_literals
import logging

import colander
from colander.polymorphism import AbstractSchema


logger = logging.getLogger(__name__)


class ApplicationRecordSchema(AbstractSchema):
    cls_type = colander.SchemaNode(colander.String())

    # TODO: this is what I think how it should work
    # need to implement a MappingSchema so that it can work like this
    __mapper_args__ = {
        'polymorphic_on': 'cls_type',
    }


class Log(ApplicationRecordSchema):
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


class Metrics(ApplicationRecordSchema):
    cls_type = 'metrics'
    values = MetricsValues()
