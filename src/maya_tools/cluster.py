"""Provide utilities related to deformers."""
import logging

from maya import cmds

__all__ = ["create"]

LOG = logging.getLogger(__name__)


def create(geometry, name="cluster"):
    # type: (str, str) -> str
    """Create a new cluster deformer.

    The difference with ``cmds.cluster()`` command is that this function will
    create the cluster and give the position to the transform node instead of
    the shape.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> cube = cmds.polyCube()[0]
        >>> cluster = create(cube + ".vtx[0]")
        >>> cmds.getAttr(cluster + ".translate")[0]
        (-0.5, -0.5, 0.5)

    Arguments:
        geometry: The target target that the cluster will affect.
        name: The name ti give ti the cluster.

    Returns:
        The name of the deformer.
    """
    old = cmds.cluster(geometry)[1]
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
    renamed = cmds.rename(new, name)  # type: str
    cmds.rename(shape, new + "Shape")
    return renamed
