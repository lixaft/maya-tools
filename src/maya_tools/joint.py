"""Joint utilities."""
from __future__ import division

import logging

from maya import cmds
from maya.api import OpenMaya

__all__ = ["parent", "auto_radius"]

LOG = logging.getLogger(__name__)


def parent(child, target):
    # type: (str, str) -> None
    """Safe parenting of a joint.

    Parent a joint by preserving the position of the child and avoiding the
    creation of a transform node between the child and the parent by maya.

    The transformation attributes of the child node must be unlocked to
    entirely preserve its position.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.createNode("joint", name="A")
        >>> b = cmds.createNode("joint", name="B")
        >>> cmds.setAttr(b + ".scale", 1, 1.1, 1)
        >>> parent(a, b)
        >>> cmds.listRelatives(a, parent=True)[0]
        'B'

    Arguments:
        child (str): The name of the node to parent.
        parent (str): The node on which the child should be parented.
    """
    mtx = cmds.xform(child, query=True, matrix=True, worldSpace=True)
    cmds.parent(child, target, relative=True)
    cmds.setAttr(child + ".jointOrient", 0, 0, 0)
    cmds.xform(child, matrix=mtx, worldSpace=True)


def auto_radius(root, method="average", multiplier=1.0, recursive=False):
    # type: (str, str, float, bool) -> None
    """Define the radius of a joint based to its distance from its children.

    Different methods can be used to find the radius:

    - ``minimum`` - Take the closest joint and generate the radius from it.
    - ``maximum`` - Ttake the joint with the maximum distance.
    - ``average`` -  Take the average of the distance of all children.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.createNode("joint")
        >>> b = cmds.createNode("joint")
        >>> c = cmds.createNode("joint")
        >>> _ = cmds.parent(b, c, a)
        >>> cmds.setAttr(c + ".translateX", 10)
        >>> auto_radius(a, recursive=True)
        >>> cmds.getAttr(a + ".radius")
        0.5

    Arguments:
        root (str): The root joint on which the radius should be set.
        method (str): The method to use in case of multiple children.
        multiplier (float): The radius multiplier.
        recursive (bool): Also affects all joints descending from the root.

    Raises:
        ValueError: The value passed to the parameter ``method`` is not valid.
    """

    def get_point(node):
        # type: (str) -> OpenMaya.MPoint
        pos = cmds.xform(node, query=True, translation=True, worldSpace=True)
        return OpenMaya.MPoint(pos)

    root_pos = get_point(root)

    # Let's find and register the distance between the root and each of its
    # children.
    distances = []
    for child in cmds.listRelatives(root, children=True, type="joint") or []:
        distances.append(root_pos.distanceTo(get_point(child)))

        # Make the recursion.
        if recursive:
            auto_radius(child, method, multiplier, recursive)

    # If not valid children are found just set the radius to 1
    if not distances:
        value = 10.0
    elif method == "average":
        value = sum(distances) / len(distances)
    elif method == "minimum":
        value = min(distances)
    elif method == "maximum":
        value = max(distances)
    else:
        raise ValueError("Invalid method value.")

    cmds.setAttr(root + ".radius", value * 0.1 * multiplier)
