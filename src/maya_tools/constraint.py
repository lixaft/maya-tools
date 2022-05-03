"""Provide utilities related to constraints."""
import logging

from maya import cmds
from maya.api import OpenMaya

__all__ = ["matrix"]

LOG = logging.getLogger(__name__)


def matrix(driver, driven, destinations=None):
    # type: (str, str, list[str] | None) -> str
    """Constraint two node using matrix nodes.

    Examples:
        >>> from maya import cmds
        >>> a = cmds.polyCube(name="A")[0]
        >>> b = cmds.polyCube(name="B")[0]
        >>> cmds.setAttr(b + ".translateX", 10)
        >>> matrix(a, b)
        'B_multMatrix'

    Arguments:
        driver (str): The name of the node that will be drive the constraint.
        driven (str): The node that will be drived by the constraint.
        destinations (list, optional): The name of the attributes on which the
            constraint will be connected to.

    Returns:
        str: The name of the `multMatrix` node used for the constraint.
    """
    # Get the driver and driven matrices.
    driver_plug = driver + ".worldMatrix[0]"
    driven_plug = driven + ".worldMatrix[0]"
    driver_matrix = OpenMaya.MMatrix(cmds.getAttr(driver_plug))
    driven_matrix = OpenMaya.MMatrix(cmds.getAttr(driven_plug))

    # Create the mult matrix that will handle the constraint.
    mult = cmds.createNode("multMatrix", name=driven + "_multMatrix")

    # Connect and set the matrix elements.
    offset = driven_matrix * driver_matrix.inverse()
    cmds.setAttr("{}.matrixIn[{}]".format(mult, 0), offset, type="matrix")
    cmds.connectAttr(driver_plug, "{}.matrixIn[{}]".format(mult, 1))
    cmds.connectAttr(
        "{}.parentInverseMatrix[0]".format(driven),
        "{}.matrixIn[{}]".format(mult, 2),
    )

    # Apply the constraint to the driven node.
    name = driven + "_decomposeMatrix"
    decompose = cmds.createNode("decomposeMatrix", name=name)
    cmds.connectAttr(mult + ".matrixSum", decompose + ".inputMatrix")
    for attribute in destinations or (x + y for x in "srt" for y in "xyz"):
        plug = "{}.{}".format(driven, attribute)
        attribute = cmds.attributeName(plug, short=True)
        cmds.connectAttr("{}.o{}".format(decompose, attribute), plug)

    return mult
