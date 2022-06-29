"""Wrap utilities."""
import logging

from maya import cmds

__all__ = ["proximity"]

LOG = logging.getLogger(__name__)


def proximity(driver, driven, falloff=1.0):
    # type: (str, str, float) -> str
    """Create a proximity wrap between two nodes.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.polySphere()[0]
        >>> b = cmds.polySphere()[0]
        >>> proximity(a, b)
        'proximityWrap1'

    Arguments:
        driver: Name of driver mesh.
        targets: List of driven meshes.
        falloff: Default value for the folloffScale attribute.

    Returns:
        The name of the deformer node.
    """
    deformer = cmds.deformer(driven, type="proximityWrap")[0]  # type: str
    plug = deformer + ".drivers[0]"
    orig = cmds.deformableShape(driver, originalGeometry=True)[0]
    if not orig:
        orig = cmds.deformableShape(driver, createOriginalGeometry=True)[0]
    cmds.connectAttr(orig, plug + ".driverBindGeometry")
    cmds.connectAttr(driver + ".worldMesh", plug + ".driverGeometry")
    cmds.setAttr(deformer + ".falloffScale", falloff)
    return deformer
