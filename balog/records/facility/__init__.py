from __future__ import unicode_literals
import datetime
import logging

import pytz
import colander

from balog.records.application import ApplicationRecordSchema
from balog.guid import GUIDFactory

LOG_GUID_FACTORY = GUIDFactory('LG')
logger = logging.getLogger(__name__)


@colander.deferred
def deferred_utcnow(node, kw):
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


@colander.deferred
def deferred_guid(node, kw):
    return LOG_GUID_FACTORY()


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
    payload = ApplicationRecordSchema()


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
