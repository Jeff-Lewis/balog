from __future__ import unicode_literals
import datetime
import logging

import pytz
import colander
import colander.polymorphism

from balog.guid import GUIDFactory


GUID_FACTORY = GUIDFactory('ET')
logger = logging.getLogger(__name__)


@colander.deferred
def deferred_utcnow(node, kw):
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


@colander.deferred
def deferred_guid(node, kw):
    return GUID_FACTORY()


class EventContext(colander.MappingSchema):

    # FQDN of the machine that generated this event
    fqdn = colander.SchemaNode(colander.String(), default=colander.drop)

    # friendly application name e.g. balanced, precog, sentry
    application = colander.SchemaNode(colander.String(), default=colander.drop)

    # build number of the application e.g. 1.0.2
    application_version = colander.SchemaNode(
        colander.String(), default=colander.drop
    )


class EventHeader(colander.MappingSchema):

    id_factory = deferred_guid

    # A unique guid assigned to this event
    id_ = colander.SchemaNode(
        colander.String(),
        name='id',
        default=id_factory,
    )

    # the channel of this event e.g. sentry.serializers.logger
    channel = colander.SchemaNode(colander.String())

    # UTC timestamp of when this event was generated
    timestamp = colander.SchemaNode(
        colander.DateTime(), default=deferred_utcnow
    )

    composition = colander.SchemaNode(colander.Bool(), default=colander.drop)

    # contextual information e.g. info about the machine and environment
    context = EventContext(default=colander.drop)


class PayloadSchema(colander.polymorphism.AbstractSchema):

    # used as a polymorphic descriminator, the cls_type is used to determine
    # what type of record to deserialize the payload as
    cls_type = colander.SchemaNode(colander.String())

    __mapper_args__ = {
        'polymorphic_on': 'cls_type',
    }


class RecordSchema(colander.MappingSchema):

    VERSION = '0.0.1'

    # version of the schema
    version = colander.SchemaNode(colander.String(), default=VERSION)

    header = EventHeader()

    payload = PayloadSchema()
