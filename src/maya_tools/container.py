"""Container utilities."""
import contextlib
import logging
from typing import Generator

from maya import cmds

LOG = logging.getLogger(__name__)

__all__ = ["add_on_create"]


@contextlib.contextmanager
def add_on_create(name):
    # type: (str) -> Generator[str, None, None]
    """Create a container that hold all the created node."""
    container = cmds.container(name=name, current=True)
    yield container
    cmds.container(container, edit=True, current=False)
