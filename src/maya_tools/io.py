"""IO stream utilities."""
import contextlib
import logging
import sys

__all__ = ["DummyStream", "silent"]

LOG = logging.getLogger(__name__)


class DummyStream(object):
    """Dummy file to silent python standard stream."""

    def write(self, _):
        """Dummy method for stream."""


@contextlib.contextmanager
def silent():
    """Silent the standard output."""
    stdout = sys.stdout
    try:
        stream = DummyStream()
        sys.stdout = stream
        yield
    finally:
        sys.stdout = stdout
