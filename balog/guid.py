from __future__ import unicode_literals
import uuid

import coid


class GUIDFactory(object):
    """Object for making prefixed GUID

    """

    def __init__(self, prefix):
        self.prefix = prefix
        self.id_codec = coid.Id(prefix=self.prefix, encoding='base58')

    def __call__(self):
        return self.id_codec.encode(uuid.uuid4())
