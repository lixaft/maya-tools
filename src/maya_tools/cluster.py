"""Provide utilities related to deformers."""
import logging

from maya import cmds

__all__ = ["create"]

LOG = logging.getLogger(__name__)


def create(obj, name=None):
    """Create a new cluster with world transformation."""
    old = cmds.cluster(obj)[1]
    new = cmds.createNode("transform", name=name)
    shape = cmds.listRelatives(old, shapes=True)[0]

    cmds.matchTransform(new, old)
    cmds.setAttr(shape + ".origin", 0, 0, 0)
    cmds.cluster(
        shape,
        edit=True,
        weightedNode=[new, new],
        bindState=True,
    )
    cmds.delete(old)
    new = cmds.rename(new, name)
    cmds.rename(shape, new + "Shape")
    return new
