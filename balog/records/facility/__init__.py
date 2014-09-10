from __future__ import unicode_literals
import datetime

import pytz
import pilo

from balog.guid import GUIDFactory


def utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


class EventContext(pilo.Form):
    fqdn = pilo.fields.String(optional=True)
    application = pilo.fields.String(optional=True)
    application_version = pilo.fields.String(optional=True)


class EventHeader(pilo.Form):
    guid_factory = GUIDFactory('LG')

    id = pilo.fields.String(default=guid_factory)
    channel = pilo.fields.String()
    timestamp = pilo.fields.Datetime(
        format='iso8601',
        default=lambda: utcnow(),
    )
    composition = pilo.fields.Boolean(default=pilo.NONE, optional=True)
    context = pilo.fields.SubForm(EventContext, optional=True)


class Payload(pilo.Form):
    pass


class FacilityRecord(pilo.Form):

    VERSION = '0.0.1'

    schema = pilo.fields.String(r'^(\d+)\.(\d+)\.(\d+)$', default=VERSION)
    header = pilo.fields.SubForm(EventHeader)
    payload = pilo.fields.SubForm(Payload)
    

if __name__ == '__main__':
    record = FacilityRecord(header=dict(channel=''), payload={})
    print record
