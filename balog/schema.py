from __future__ import unicode_literals
import collections
import datetime
import json

from .guid import GUIDFactory


class LogSchema(object):
    # the schema for the logging format
    SCHEMA = 0

    guid_factory = GUIDFactory('LG')

    @classmethod
    def jsonify_unstructed_log(cls, record):
        """Jsonify a Python logging library record

        """
        channel = record.name
        # TODO: maybe we should get created time from record instead?
        now = datetime.datetime.utcnow()
        event_dict = collections.OrderedDict([
            ('guid', cls.guid_factory()),
            ('type', 'unstructed-log'),
            ('channel', channel),
            ('timestamp', now.isoformat()),
            ('meta', dict(level=record.levelname.lower())),
            ('data', dict(message=record.getMessage())),
            ('schema', cls.SCHEMA),
        ])
        return json.dumps(event_dict)

    def __call__(self, logger, name, event_dict):
        """Transform given event dict to the format we want

        """
        channel = event_dict.pop('channel', None)
        if channel is None:
            channel = logger.name + '.' + event_dict.pop('event')
        now = datetime.datetime.utcnow()
        new_event_dict = collections.OrderedDict([
            # universal guid of event
            ('guid', self.guid_factory()),
            # event type
            ('type', 'log'),
            # channel of the event
            ('channel', channel),
            # timestamp of this event
            ('timestamp', now.isoformat()),
            # meta here is the data about the event, for the log event,
            # the logging level is then an attribute in meta field
            ('meta', dict(level=name)),
            # this is the payload for event
            ('data', event_dict.copy()),
            # schema version of event format
            ('schema', self.SCHEMA),
        ])
        return new_event_dict
