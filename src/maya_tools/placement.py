"""Contain utilities around position."""
from __future__ import division

import logging
from typing import List

from maya import cmds
import maya_tools.api

__all__ = []

LOG = logging.getLogger(__name__)


def distribute(nodes):
    # type: (List[str]) -> None
    """Equally distribute the position of the given nodes.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.createNode("transform")
        >>> b = cmds.createNode("transform")
        >>> c = cmds.createNode("transform")
        >>> cmds.setAttr(c + ".translateY", 5)
        >>> distribute([a, b, c])
        >>> cmds.getAttr(b + ".translateY")
        2.5

    Arguments:
        nodes: The nodes to move.
    """
    first = maya_tools.api.get_point(nodes[0])
    last = maya_tools.api.get_point(nodes[-1])

    offset = (last - first) * (1 / (len(nodes) - 1))

    previous = first
    for node in nodes[1:-1]:
        cmds.xform(
            node,
            translation=previous + offset,
            worldSpace=True,
        )
        previous += offset
