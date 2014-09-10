from __future__ import unicode_literals
import datetime

import pytz

from balog.guid import GUIDFactory


class FacilityRecord(object):

    VERSION = '0.0.1'

    guid_factory = GUIDFactory('LG')

    def __init__(
        self,
        channel,
        payload,
        guid=None,
        timestamp=None,
        schema=None,
        open_content=None,
        context=None,
    ):
        self.id = guid
        if self.id is None:
            self.id = self.guid_factory()
        self.channel = channel
        self.payload = payload
        self.timestamp = timestamp
        if self.timestamp is None:
            self.timestamp = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        self.schema = schema
        if self.schema is None:
            self.schema = self.VERSION
        self.open_content = open_content
        self.context = context

    def to_dict(self):
        """Convert the record to a dict format

        """
        payload = self.payload
        if not isinstance(payload, dict):
            payload = payload.to_dict()
        result = dict(
            id=self.id,
            channel=self.channel,
            timestamp=self.timestamp.isoformat(),
            schema=self.schema,
            payload=payload,
        )
        if self.open_content is not None:
            result['open_content'] = self.open_content
        if self.context is not None:
            result['context'] = self.context
        return result
