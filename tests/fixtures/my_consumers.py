from __future__ import unicode_literals

from balog.consumers import consumer_config


@consumer_config(topic='foo.bar', cls_types=('eggs', ))
def consumer_a(events):
    pass


@consumer_config(topic='spam.eggs')
def consumer_b(events):
    pass
