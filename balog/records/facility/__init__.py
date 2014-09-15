from __future__ import unicode_literals
import datetime

import pytz
import colander

from balog.guid import GUIDFactory

LOG_GUID_FACTORY = GUIDFactory('LG')


@colander.deferred
def deferred_utcnow(node, kw):
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


@colander.deferred
def deferred_guid(node, kw):
    return LOG_GUID_FACTORY()


class Abstract(colander.Mapping):

    def serialize(self, node, appstruct, not_abstract=False):
        if not_abstract:
            return super(Abstract, self).serialize(node, appstruct)
        polymorphic_on = node.__mapper_args__['polymorphic_on']
        polymorphic_id = appstruct[polymorphic_on.name]

        # TODO: get polymorphic_id mapping to subclasses
        if polymorphic_id == 'log':
            subnode = Log()
        return subnode.typ.serialize(subnode, appstruct, not_abstract=True)

    def deserialize(self, node, cstruct, not_abstract=False):
        if not_abstract:
            return super(Abstract, self).deserialize(node, cstruct)
        polymorphic_on = node.__mapper_args__['polymorphic_on']
        polymorphic_id = cstruct[polymorphic_on.name]

        # TODO: get polymorphic_id mapping to subclasses
        if polymorphic_id == 'log':
            subnode = Log()
        return subnode.typ.deserialize(subnode, cstruct, not_abstract=True)


class AbstractSchema(colander.SchemaNode):
    schema_type = Abstract


class Payload(AbstractSchema):
    type = colander.SchemaNode(colander.String())

    # TODO: this is what I think how it should work
    # need to implement a MappingSchema so that it can work like this
    __mapper_args__ = {
        'polymorphic_on': type
    }


class Log(Payload):
    type = 'log'
    message = colander.SchemaNode(colander.String())
    severity = colander.SchemaNode(colander.String(), validators=[
        colander.OneOf((
            'debug',
            'info',
            'warning',
            'error',
        ))
    ])


class EventContext(colander.MappingSchema):
    fqdn = colander.SchemaNode(colander.String(), default=colander.drop)
    application = colander.SchemaNode(colander.String(), default=colander.drop)
    application_version = colander.SchemaNode(colander.String(), default=colander.drop)


class EventHeader(colander.MappingSchema):
    id = colander.SchemaNode(colander.String(), default=deferred_guid)
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
            'type': 'log',
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
            'type': 'log',
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
            'type': 'log',
            'message': 'bar',
            'severity': 'info',
        }
    })
