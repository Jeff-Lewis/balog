from __future__ import unicode_literals
import uuid

from .base58 import b58encode


class GUIDFactory(object):
    """Object for making prefixed GUID

    """

    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self):
        return self.prefix + b58encode(uuid.uuid4().bytes)
