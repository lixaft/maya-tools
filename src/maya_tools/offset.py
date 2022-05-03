"""Provide utilities related to offsets."""
import logging
import math

from maya import cmds
from maya.api import OpenMaya

import maya_tools._internal

__all__ = [
    "group",
    "inverse_group",
    "matrix",
    "matrix_to_group",
    "reset_matrix",
    "unmatrix",
]

LOG = logging.getLogger(__name__)


def group(node, suffix="offset"):
    """Create a group above the node with the same transformation values.

    Arguments:
        node (str): The node which create the offset group.
        suffix (str): The suffix of the offset group.

    Returns:
        str: The offset node name.
    """
    offset = cmds.createNode(
        "transform",
        name="{}_{}".format(node, suffix),
        parent=(cmds.listRelatives(node, parent=True) or [None])[0],
    )
    cmds.matchTransform(offset, node)
    cmds.parent(node, offset)
    return offset


def inverse_group(node):
    """Create an offset that cancel the transformation values of the nodes.

    Arguments:
        node (str): The node which create the inverse offset.

    Returns:s
        str: The offset node name.
    """
    inverse = group(node, suffix="inverse")
    offset = group(inverse)
    offset = cmds.rename(offset, node + "_offset")
    # ftd.graph.matrix_to_srt(node + ".inverseMatrix", inverse)
    return offset


@maya_tools._internal.with_maya(minimum=2020)
def matrix(node):
    """Transfer the transformation to the offsetParentMatrix attribute.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> cmds.setAttr(node + ".translateY", 5)
        >>> matrix(node)
        >>> cmds.getAttr(node + ".translateY")
        0.0
        >>> cmds.getAttr(node + ".offsetParentMatrix")[-3]
        5.0

    Arguments:
        node (str): The name of the node to offset.
    """
    matrix_ = OpenMaya.MMatrix(cmds.getAttr(node + ".worldMatrix[0]"))
    parent = OpenMaya.MMatrix(cmds.getAttr(node + ".parentInverseMatrix[0]"))
    cmds.setAttr(node + ".offsetParentMatrix", matrix_ * parent, type="matrix")
    cmds.setAttr(node + ".translate", 0, 0, 0)
    cmds.setAttr(node + ".rotate", 0, 0, 0)
    cmds.setAttr(node + ".scale", 1, 1, 1)
    cmds.setAttr(node + ".shear", 0, 0, 0)


def reset_matrix(node):
    """Reset the offsetParentMatrix attribute to identity.

    Arguments:
        node (str): The node to reset.
    """
    matrix_ = OpenMaya.MMatrix()
    cmds.setAttr(node + ".offsetParentMatrix", matrix_, type="matrix")


def unmatrix(node):
    """Transfer the transformation to the translate/rotate/scale attributes.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> from maya.api import OpenMaya
        >>> node = cmds.createNode("transform")
        >>> matrix = OpenMaya.MMatrix()
        >>> matrix[-3] = 5
        >>> cmds.setAttr(node + ".offsetParentMatrix", matrix, type="matrix")
        >>> unmatrix(node)
        >>> cmds.getAttr(node + ".translateY")
        5.0

    Arguments:
        node (str): The target node.
    """
    matrix_ = OpenMaya.MMatrix(cmds.getAttr(node + ".worldMatrix[0]"))
    identity = OpenMaya.MMatrix.kIdentity
    transform = OpenMaya.MTransformationMatrix(matrix_)
    space = OpenMaya.MSpace.kTransform

    cmds.setAttr(node + ".translate", *transform.translation(space))
    cmds.setAttr(node + ".rotate", *map(math.degrees, transform.rotation()))
    cmds.setAttr(node + ".scale", *transform.scale(space))
    cmds.setAttr(node + ".shear", *transform.shear(space))
    cmds.setAttr(node + ".offsetParentMatrix", identity, type="matrix")
