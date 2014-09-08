from __future__ import unicode_literals
import logging
import json

from .schema import LogSchema


class SchemaFormatter(logging.Formatter):
    """Logging formatter for making sure record are turned into defined json
    schema

    """

    def format(self, record):
        record.message = record.getMessage()
        msg = record.message
        try:
            json.loads(msg)
        # looks like we have a plain text string message
        except ValueError:
            # transform it into log schema
            msg = LogSchema.jsonify_unstructed_log(record)
        return msg
