from __future__ import unicode_literals
import colander

from balog.records import base
from balog.guid import GUIDFactory


GUID_FACTORY = GUIDFactory('LG')


@colander.deferred
def deferred_guid(node, kw):
    return GUID_FACTORY()


class LoggingEventHeader(base.EventHeader):

    # A unique guid assigned to this event
    id_ = colander.SchemaNode(
        colander.String(),
        name='id',
        default=deferred_guid,
    )


class FacilityRecordSchema(base.RecordSchema):

    header = LoggingEventHeader()
