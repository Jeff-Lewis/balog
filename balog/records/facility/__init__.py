from __future__ import unicode_literals
import datetime

import pytz
import colander

from balog.guid import GUIDFactory


def utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


class EventHeader(colander.MappingSchema):
    guid_factory = GUIDFactory('LG')

    id = colander.SchemaNode(colander.String(), default=guid_factory)
    channel = colander.SchemaNode(colander.String())
    timestamp = colander.SchemaNode(colander.DateTime(), default=utcnow)
    composition = colander.SchemaNode(colander.Bool(), default=colander.drop)
    # context = pilo.fields.SubForm(EventContext, optional=True)


class FacilityRecordSchema(colander.MappingSchema):

    VERSION = '0.0.1'

    schema = colander.SchemaNode(colander.String())
    header = EventHeader()
    #payload = pilo.fields.SubForm(Payload)
    

if __name__ == '__main__':
    record = FacilityRecordSchema()
    print record.deserialize({
        'schema': 'hello',
        'header': {
            'id': 'foobar',
            'channel': 'test',
            'timestamp': '2014-08-26T04:15:53.386960+00:00',
        },
    })
    #import ipdb; ipdb.set_trace()
