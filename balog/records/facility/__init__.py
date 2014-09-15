from __future__ import unicode_literals
import datetime

import pytz
import colander

from balog.guid import GUIDFactory


@colander.deferred
def deferred_utcnow(node, kw):
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


@colander.deferred
def deferred_guid(node, kw):
    return GUIDFactory('LG')()


class EventHeader(colander.MappingSchema):
    guid_factory = GUIDFactory('LG')

    id = colander.SchemaNode(colander.String(), default=deferred_guid)
    channel = colander.SchemaNode(colander.String())
    timestamp = colander.SchemaNode(colander.DateTime(), default=deferred_utcnow)
    composition = colander.SchemaNode(colander.Bool(), default=colander.drop)
    # context = pilo.fields.SubForm(EventContext, optional=True)


class FacilityRecordSchema(colander.MappingSchema):

    VERSION = '0.0.1'

    schema = colander.SchemaNode(colander.String(), default=VERSION)
    header = EventHeader()
    #payload = pilo.fields.SubForm(Payload)
    

if __name__ == '__main__':
    schema = FacilityRecordSchema()
    print schema.bind().serialize({'header': {'channel': 'foobar'}})
    print schema.deserialize({
        'schema': 'hello',
        'header': {
            'id': 'foobar',
            'channel': 'test',
            'timestamp': '2014-08-26T04:15:53.386960+00:00',
        },
    })
    #import ipdb; ipdb.set_trace()
