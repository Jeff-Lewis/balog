from __future__ import unicode_literals

from balog.consumers import consumer_config


@consumer_config(topic='foo.bar', cls_type='eggs')
def consumer_a(event):
    pass


@consumer_config(topic='spam.eggs')
def consumer_b(event):
    pass


@consumer_config(topic='5566', cls_type=('55', '66'))
def consumer_c(event):
    pass


# no overlap in cls type with c
@consumer_config(topic='5566', cls_type=('77', '88'))
def consumer_d(event):
    pass


# overlap in cls type with d and e
@consumer_config(topic='5566', cls_type=('66', '88'))
def consumer_e(event):
    pass


all_consumers = consumer_a, consumer_b, consumer_c, consumer_d, consumer_e
