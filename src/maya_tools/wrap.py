"""Wrap utilities."""
import logging

from maya import cmds

__all__ = ["proximity"]

LOG = logging.getLogger(__name__)


def proximity(driver, driven, falloff=1.0):
    """Create a proximity wrap between two nodes.

    Arguments:
        driver (str): Name of driver mesh.
        targets (list): List of driven meshes.
        falloff (float): Default value for the folloffScale attribute.

    Returns:
        str: The name of the deformer node.
    """
    deformer = cmds.deformer(driven, type="proximityWrap")[0]
    plug = deformer + ".drivers[0]"
    orig = cmds.deformableShape(driver, originalGeometry=True)[0]
    if not orig:
        orig = cmds.deformableShape(driver, createOriginalGeometry=True)[0]
    cmds.connectAttr(orig, plug + ".driverBindGeometry")
    cmds.connectAttr(driver + ".worldMesh", plug + ".driverGeometry")
    cmds.setAttr(deformer + ".falloffScale", falloff)
    return deformer
