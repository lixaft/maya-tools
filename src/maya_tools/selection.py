"""Utilities related to selection."""
import contextlib
import logging
from typing import Generator, List

from maya import cmds
from maya.api import OpenMaya, OpenMayaUI

__all__ = ["from_viewport", "keep"]
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
    # type: () -> Generator[List[str], None, None]
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
