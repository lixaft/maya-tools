"""Utilities related to selection."""
import contextlib
import itertools
import logging
from typing import Generator, Optional, Sequence

from maya import cmds
from maya.api import OpenMaya, OpenMayaUI

__all__ = ["from_viewport", "keep", "mirror"]
LOG = logging.getLogger(__name__)


def from_viewport():  # pragma: no cover
    # type: () -> None
    """Select all the visible object inside the active viewport.

    This cannot be executed with maya standalone as there is no viewport.
    """
    viewport = OpenMayaUI.M3dView.active3dView()
    OpenMaya.MGlobal.selectFromScreen(
        0,
        0,
        viewport.portWidth(),
        viewport.portHeight(),
        OpenMaya.MGlobal.kReplaceList,
        OpenMaya.MGlobal.kWireframeSelectMethod,
    )


@contextlib.contextmanager
def keep():
    # type: () -> Generator[list[str], None, None]
    """Preserve the selection during the execution.

    This will store the current selection, execute the given block and then
    restore the stored selection.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> _ = cmds.createNode("transform", name="A")
        >>> cmds.ls(selection=True)
        ['A']
        >>> with keep():
        ...     _ = cmds.createNode("transform", name="B")
        >>> cmds.ls(selection=True)
        ['A']

    Yields:
        The name of the current selected nodes.:w
    """
    selection = cmds.ls(selection=True)
    try:
        yield selection
    finally:
        if selection:
            cmds.select(selection)
        else:
            cmds.select(clear=True)


def mirror(node, patterns=("L_:R_", "l_:r_")):
    # type: (str, Sequence[str]) -> Optional[str]
    """Find the opposite of the specified node.

    The function will search for a pattern in the given node name. If a match
    is found, the opposite pattern will be used to check if the corresponding
    node exists in the scene.

    A pattern consists of a string divided into two parts separated by the
    character `:` (the order does not matter). One is the pattern that should
    be searched for in the given node and the other will be the one with which
    the opposite will be searched.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> _ =cmds.createNode("transform", name="L_a")
        >>> _ = cmds.createNode("transform", name="R_a")
        >>> mirror("L_a")
        'R_a'

    Arguments:
        node: The node for which the opposite will be searched.
        pattern:

    Returns:
        The name of the opposite node or None in the case where nothing as
        been found.
    """
    for pattern in patterns:
        right, left = pattern.split(":")
        for current, opposite in itertools.permutations((left, right)):
            if current not in node:
                continue

            opposite_node = node.replace(current, opposite)
            return opposite_node if cmds.objExists(opposite_node) else None
    return None
