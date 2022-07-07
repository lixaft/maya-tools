"""Shape related utilities."""
import logging
from typing import Optional, cast

from maya import cmds

__all__ = ["get_orig", "clean_orig"]

LOG = logging.getLogger(__name__)


def get_orig(shape):
    # type: (str) -> str
    """Return the orig shape associated to the given shape.

    In the case where the given shape doesn't have any orig shape, create one
    and return it.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> geo = cmds.polySphere(constructionHistory=False)[0]
        >>> shape = cmds.listRelatives(geo, shapes=True)[0]
        >>> get_orig(shape)
        'pSphereShape1Orig'
        >>> get_orig(shape)
        'pSphereShape1Orig'

    Arguments:
        shape (str): The name source shape.

    Returns:
        str: The name of the associated orig shape.
    """
    orig = cmds.deformableShape(shape, originalGeometry=True)[0]
    if not orig:
        orig = cmds.deformableShape(shape, createOriginalGeometry=True)[0]
    return cast(str, orig.split(".")[0])


def clean_orig(node=None):
    # type: (Optional[str]) -> None
    """Clean the unused orig shapes.

    If no arguments is specified, operate on all nodes in the scene.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> geo = cmds.polySphere(constructionHistory=False)[0]
        >>> shape = cmds.listRelatives(geo, shapes=True)[0]
        >>> _ = cmds.deformableShape(shape, createOriginalGeometry=True)[0]
        >>> clean_orig(geo)
        >>> cmds.ls(geo, intermediateObjects=True, dagObjects=True)
        []

    Arguments:
        node (str, optional): The name of the node that need to be cleaned.
    """
    args = [node] if node else []
    shapes = cmds.ls(*args, intermediateObjects=True, dagObjects=True)
    for shape in shapes or []:
        if not cmds.listConnections(shape, type="groupParts"):
            cmds.delete(shape)
