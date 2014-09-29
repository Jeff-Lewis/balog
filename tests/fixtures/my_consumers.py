from __future__ import unicode_literals

from balog.consumers import consumer_config


@consumer_config(topic='foo.bar', cls_types='eggs')
def consumer_a(event):
    pass


@consumer_config(topic='spam.eggs')
def consumer_b(event):
    pass


@consumer_config(topic='5566', cls_types=('55', '66'))
def consumer_c(event):
    pass
