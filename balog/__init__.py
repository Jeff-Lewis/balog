from __future__ import unicode_literals

import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import format_exc_info
from structlog.processors import JSONRenderer

from schema import LogSchema


def configure():
    """Configure Balanced logging system

    """
    structlog.configure(
        processors=[
            format_exc_info,
            LogSchema(),
            JSONRenderer(),
        ],
        logger_factory=LoggerFactory(),
    )


def get_logger(*args, **kwargs):
    """Get and return the logger

    """
    return structlog.get_logger(*args, **kwargs)
