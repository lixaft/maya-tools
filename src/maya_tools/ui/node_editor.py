"""Node editor utilities."""
import contextlib
import logging
from typing import Generator

from maya import cmds, mel

LOG = logging.getLogger(__name__)

__all__ = ["lock"]


@contextlib.contextmanager
def lock():
    # type: () -> Generator[None, None, None]
    """Prevents adding new nodes in the Node Editor.

    This context manager can be useful when building rigs as adding nodes to
    the editor at creation can be very time consuming when many nodes are
    generated at the same time.
    """
    panel = mel.eval("getCurrentNodeEditor")
    previous = cmds.nodeEditor(panel, query=True, addNewNodes=True)
    cmds.nodeEditor(panel, edit=True, addNewNodes=False)
    yield
    cmds.nodeEditor(panel, edit=True, addNewNodes=previous)
