from __future__ import unicode_literals
import datetime
import logging

import pytz
import colander

from balog.guid import GUIDFactory

LOG_GUID_FACTORY = GUIDFactory('LG')
logger = logging.getLogger(__name__)


@colander.deferred
def deferred_utcnow(node, kw):
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


@colander.deferred
def deferred_guid(node, kw):
    return LOG_GUID_FACTORY()


def get_root_class(bases, super_cls):
    """Get root class which has super_cls in base classes

    """
    bases_set = set(bases)
    root_cls = None
    while root_cls is None and bases_set:
        next_bases_set = set()
        for base_cls in bases_set:
            if AbstractSchema in base_cls.__bases__:
                root_cls = base_cls
                break
            next_bases_set |= set(base_cls.__bases__)
        bases_set = next_bases_set
    return root_cls


class _AbstractMeta(colander._SchemaMeta):
    def __init__(cls, name, bases, clsattrs):
        def super_init():
            return super(_AbstractMeta, cls).__init__(name, bases, clsattrs)
        # AbstractSchema class, skip
        if bases == (colander.SchemaNode, ):
            return super_init()
        # this class inherts Abstract as parent
        if AbstractSchema in bases:
            if '__mapper_args__' not in clsattrs:
                raise TypeError('__mapper_args__ should be defined')
            if 'polymorphic_on' not in clsattrs['__mapper_args__']:
                raise TypeError('__mapper_args__ should has polymorphic_on')
            cls.__polymorphic_mapping__ = {}
        else:
            # find the root class, for example:
            #     + AbstractSchema
            #         + root
            #             + foo
            #                 + bar
            # so the root class will be `root`
            root_cls = get_root_class(bases, AbstractSchema)
            # register this class to root class
            polymorphic_on = root_cls.__mapper_args__['polymorphic_on']
            polymorphic_id = clsattrs[polymorphic_on.name]
            root_cls.__polymorphic_mapping__[polymorphic_id] = cls
            
            logger.info(
                'Register class %s to root class %s as %s',
                cls, root_cls, polymorphic_id,
            )
        return super_init()


class Abstract(colander.Mapping):

    def _get_subnode(self, node, data):
        polymorphic_on = node.__mapper_args__['polymorphic_on']
        polymorphic_id = data[polymorphic_on.name]
        root_cls = get_root_class((node.__class__, ), AbstractSchema)
        cls = root_cls.__polymorphic_mapping__[polymorphic_id]
        subnode = cls()
        return subnode

    def serialize(self, node, appstruct, not_abstract=False):
        if not_abstract:
            return super(Abstract, self).serialize(node, appstruct)
        subnode = self._get_subnode(node, appstruct)
        return subnode.typ.serialize(subnode, appstruct, not_abstract=True)

    def deserialize(self, node, cstruct, not_abstract=False):
        if not_abstract:
            return super(Abstract, self).deserialize(node, cstruct)
        subnode = self._get_subnode(node, cstruct)
        return subnode.typ.deserialize(subnode, cstruct, not_abstract=True)


class AbstractSchema(colander.SchemaNode):
    __metaclass__ = _AbstractMeta
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


class SuperLog(Log):
    type = 'super_log'
    super = colander.SchemaNode(colander.Bool())


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

    print schema.bind().serialize({
        'header': {
            'channel': 'foobar',
            'context': {
                'fqdn': 'justitia.vandelay.io',
            }
        },
        'payload': {
            'type': 'super_log',
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
            'type': 'super_log',
            'message': 'bar',
            'severity': 'info',
            'super': True,
        }
    })
