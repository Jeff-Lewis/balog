from __future__ import unicode_literals
import logging

import balog


logger = logging.getLogger('sample consumer')


@balog.consumer_config(topic='test')
def on_event(event):
    logger.info('test %s', event)
