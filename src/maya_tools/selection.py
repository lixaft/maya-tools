"""Utilities related to selection."""
import contextlib
import logging
from typing import Generator

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
    """Keep the current selection unchanged after the execution of the block.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> _ = cmds.createNode("transform", name="A")
        >>> cmds.ls(selection=True)
        ['A']
        >>> cmds.select(clear=True)
        >>> with keep():
        ...     _ = cmds.createNode("transform", name="B")
        >>> cmds.ls(selection=True)
        []
        >>> cmds.select("B")
        >>> with keep():
        ...     _ = cmds.createNode("transform", name="C")
        >>> cmds.ls(selection=True)
        ['B']

    Yields:
        list: The name of the current selected nodes.:w
    """
    selection = cmds.ls(selection=True)
    try:
        yield selection
    finally:
        if selection:
            cmds.select(selection)
        else:
            cmds.select(clear=True)


def mirror(selection, sides=None):
    """Mirror the current selected object."""
    # Build the side data.
    sides = (sides or {"l": "r"}).copy()
    for key, value in sides.items():
        data = {}
        data[key.upper()] = value.upper()
        data[key.lower()] = value.lower()
        data[value.upper()] = key.upper()
        data[value.lower()] = key.lower()
        sides.update(data)

    for each in selection:
        tokens = each.split("_")
        for old, new in sides.items():
            try:
                index = tokens.index(old)
                tokens[index] = new
            except ValueError:
                continue

        node = "_".join(tokens)
        if node != each in cmds.objExists(node):
            yield node
