"""IO stream utilities."""
import contextlib
import logging
import os
import sys
from typing import Generator

__all__ = ["silent"]

LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def silent():
    # type: () -> Generator[None, None, None]
    """Silent the standard output."""
    stdout = sys.stdout
    try:
        with open(os.devnull, "a") as stream:
            sys.stdout = stream
        yield
    finally:
        sys.stdout = stdout
