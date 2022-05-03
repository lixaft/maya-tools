"""Cleanup utilities."""
import logging

from maya import mel

__all__ = ["delete_unused"]

LOG = logging.getLogger(__name__)


def delete_unused():
    # type: () -> None
    """Delete all the unused nodes in the scene.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("addDoubleLinear")
        >>> delete_unused()
        >>> cmds.objExists(node)
        False
    """
    mel.eval("MLdeleteUnused")
