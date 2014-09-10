from __future__ import unicode_literals
import datetime

import pytz
import pilo

from balog.guid import GUIDFactory


def utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


class EventContext(pilo.Form):
    pass


class EventHeader(pilo.Form):
    guid_factory = GUIDFactory('LG')

    id = pilo.fields.String(default=guid_factory)
    channel = pilo.fields.String()
    timestamp = pilo.fields.Datetime(
        format='iso8601',
        default=lambda: utcnow(),
    )
    context = pilo.fields.SubForm(EventContext, optional=True)


class FacilityRecord(pilo.Form):

    VERSION = '0.0.1'

    schema = pilo.fields.String(r'^(\d+)\.(\d+)\.(\d+)$', default=VERSION)
    header = pilo.fields.SubForm(EventHeader)
    

if __name__ == '__main__':
    record = FacilityRecord(header=dict(channel='', timestamp=utcnow().isoformat()))
    print record
