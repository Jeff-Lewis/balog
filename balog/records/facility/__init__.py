from __future__ import unicode_literals
import datetime
import logging

import pytz
import colander
from colander.polymorphism import AbstractSchema

from balog.guid import GUIDFactory

LOG_GUID_FACTORY = GUIDFactory('LG')
logger = logging.getLogger(__name__)


@colander.deferred
def deferred_utcnow(node, kw):
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


@colander.deferred
def deferred_guid(node, kw):
    return LOG_GUID_FACTORY()


class Payload(AbstractSchema):
    cls_type = colander.SchemaNode(colander.String())

    # TODO: this is what I think how it should work
    # need to implement a MappingSchema so that it can work like this
    __mapper_args__ = {
        'polymorphic_on': 'cls_type',
    }


class Log(Payload):
    cls_type = 'log'
    message = colander.SchemaNode(colander.String())
    severity = colander.SchemaNode(colander.String(), validators=[
        colander.OneOf((
            'debug',
            'info',
            'warning',
            'error',
        ))
    ])


class SuperLog(Log):
    cls_type = 'super_log'
    super = colander.SchemaNode(colander.Bool())


class EventContext(colander.MappingSchema):
    fqdn = colander.SchemaNode(colander.String(), default=colander.drop)
    application = colander.SchemaNode(colander.String(), default=colander.drop)
    application_version = colander.SchemaNode(colander.String(), default=colander.drop)


class EventHeader(colander.MappingSchema):
    id_ = colander.SchemaNode(
        colander.String(),
        name='id',
        default=deferred_guid,
    )
    channel = colander.SchemaNode(colander.String())
    timestamp = colander.SchemaNode(colander.DateTime(), default=deferred_utcnow)
    composition = colander.SchemaNode(colander.Bool(), default=colander.drop)
    context = EventContext(default=colander.drop)


class FacilityRecordSchema(colander.MappingSchema):
    VERSION = '0.0.1'

    schema = colander.SchemaNode(colander.String(), default=VERSION)
    header = EventHeader()
    payload = Payload()


if __name__ == '__main__':
    schema = FacilityRecordSchema()

    print schema.bind().serialize({
        'header': {
            'channel': 'foobar'
        },
        'payload': {
            'cls_type': 'log',
            'message': 'bar',
            'severity': 'info',
        }
    })
    print schema.bind().serialize({
        'header': {
            'channel': 'foobar',
            'context': {
                'fqdn': 'justitia.vandelay.io',
            }
        },
        'payload': {
            'cls_type': 'log',
            'message': 'bar',
            'severity': 'info',
        }
    })

    print schema.deserialize({
        'schema': 'hello',
        'header': {
            'id': 'foobar',
            'channel': 'test',
            'timestamp': '2014-08-26T04:15:53.386960+00:00',
        },
        'payload': {
            'cls_type': 'log',
            'message': 'bar',
            'severity': 'info',
        }
    })

    print schema.bind().serialize({
        'header': {
            'channel': 'foobar',
            'context': {
                'fqdn': 'justitia.vandelay.io',
            }
        },
        'payload': {
            'cls_type': 'super_log',
            'message': 'bar',
            'severity': 'info',
            'super': True,
        }
    })
    print schema.deserialize({
        'schema': 'hello',
        'header': {
            'id': 'foobar',
            'channel': 'test',
            'timestamp': '2014-08-26T04:15:53.386960+00:00',
        },
        'payload': {
            'cls_type': 'super_log',
            'message': 'bar',
            'severity': 'info',
            'super': True,
        }
    })
