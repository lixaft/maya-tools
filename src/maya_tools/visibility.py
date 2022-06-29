"""Visibility modules."""
import logging

from maya import cmds

__all__ = ["is_visible"]

LOG = logging.getLogger(__name__)


def is_visible(node):
    # type: (str) -> bool
    """Check if the node is visible by querying all its ancestors.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.createNode("transform", name="A")
        >>> b = cmds.createNode("transform", name="B", parent=a)
        >>> cmds.setAttr(a + ".visibility", False)
        >>> cmds.getAttr(b + ".visibility")
        True
        >>> is_visible(b)
        False

        By turning on the visibility of the parent of the node, it will become
        visible inside the viewport and this function will return True:

        >>> cmds.setAttr(a + ".visibility", True)
        >>> is_visible(b)
        True

    Arguments:
        node: The node to check.

    Returns:
        True if the node is visible, False otherwise.
    """
    path = cmds.ls(node, long=True)[0]
    while "|" in path:
        path, tail = path.rsplit("|", 1)
        visible = cmds.getAttr(tail + ".visibility")
        if not visible:
            return False
    return True
