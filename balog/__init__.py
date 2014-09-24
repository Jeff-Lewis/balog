from __future__ import unicode_literals
import os

import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import format_exc_info
from structlog.processors import JSONRenderer

from .processors import LogProcessor


def load_pkg_file(pkg_filename, filename, default):
    """Load file content under package folder

    """
    pkg_dir = os.path.dirname(pkg_filename)
    filepath = os.path.join(pkg_dir, filename)
    try:
        with open(filepath, 'rt') as pkg_file:
            return pkg_file.read().strip()
    except IOError:
        return default

__version__ = load_pkg_file(__file__, 'version.txt', '0.0.0')


def configure():
    """Configure Balanced logging system

    """
    structlog.configure(
        processors=[
            format_exc_info,
            LogProcessor(),
            JSONRenderer(),
        ],
        logger_factory=LoggerFactory(),
    )


def get_logger(*args, **kwargs):
    """Get and return the logger

    """
    return structlog.get_logger(*args, **kwargs)
