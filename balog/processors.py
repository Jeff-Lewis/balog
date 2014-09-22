from __future__ import unicode_literals
import json

from .records.facility import FacilityRecordSchema


class LogProcessor(object):

    @classmethod
    def jsonify_unstructed_log(cls, record):
        """Jsonify a Python logging library record

        """
        channel = record.name
        schema = FacilityRecordSchema()
        event_dict = schema.bind().serialize({
            'header': {
                'channel': channel,
                'context': {
                    # TODO: add application information?
                }
            },
            'payload': {
                'cls_type': 'log',
                'severity': record.levelname.lower(),
                'message': record.getMessage(),
            }
        })
        if record.exc_text:
            event_dict['payload']['exc_text'] = record.exc_text
        return json.dumps(event_dict)

    def __call__(self, logger, name, event_dict):
        """Transform given event dict to the format we want

        """
        channel = event_dict.pop('channel', None)
        if channel is None:
            channel = logger.name + '.' + event_dict.pop('event')
        schema = FacilityRecordSchema()
        new_event_dict = schema.bind().serialize({
            'header': {
                'channel': channel,
                'context': {
                    # TODO: add application information?
                }
            },
            'payload': event_dict['payload']
        })
        return new_event_dict
