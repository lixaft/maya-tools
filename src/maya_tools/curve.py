"""Provide utilities related to curves."""
from __future__ import division

import logging
from typing import Any

from maya import cmds
from maya.api import OpenMaya

__all__ = [
    "from_points",
    "from_transforms",
    "get_cached",
    "get_points",
    "replace",
    "set_cached",
    "transform",
]

LOG = logging.getLogger(__name__)


def get_points(curve, world=False, method="cv"):
    # type: (str, bool, str) -> list[tuple[float, float, float]]
    """Query the position of each control points of a curve.

    Its possible to query either ``cv`` and ``ep`` points using the ``method``
    parameter.

    Examples:
        >>> from maya import cmds
        >>> node = cmds.curve(
        ...     point=[(-5, 0, 0), (0, 5, 0), (5, 0, 0)],
        ...     degree=1,
        ... )
        >>> cmds.setAttr(node + ".translateZ", -2)
        >>> get_points(node, world=True)
        [(-5.0, 0.0, -2.0), (0.0, 5.0, -2.0), (5.0, 0.0, -2.0)]

    Arguments:
        curve (str): The name of the curve node to query.
        world (bool): Specify on which space the coordinates will be returned.
        method (str): Which type of points should be queried.

    Returns:
        list: A two-dimensional array that contains all the positions of the
        points that compose the curve.
    """
    pos = cmds.xform(
        "{}.{}[*]".format(curve, method),
        query=True,
        translation=True,
        worldSpace=world,
    )
    # Build an array with each point position in it's own x, y, z array.
    points = [tuple(pos[x * 3 : x * 3 + 3]) for x, _ in enumerate(pos[::3])]
    return points  # type: ignore


def get_cached(curve):
    # type: (str) -> list[int | bool | list[float]]
    """Extract the data contained in the .cached attribute.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> curve = cmds.curve(
        ...     point=[(-5, 0, 0), (0, 5, 0), (5, 0, 0)],
        ...     degree=1,
        ... )
        >>> get_cached(curve)
        [1, 2, 0, False, 3, [0, 1, 2], 3, 3, ...]

    Arguments:
        curve (str): The the curve from which the data should be extracted.

    Returns:
        list: The curve data as a list.
    """
    sel = OpenMaya.MSelectionList()
    sel.add(curve + ".cached")
    plug = sel.getPlug(0)

    cmd = [x.strip().split() for x in plug.getSetAttrCmds()[1:-1]]

    # Add base.
    args = []  # type: list[int | bool | list[float]]
    args.extend([int(x) for x in cmd[0][:3] + [cmd[0][-1]]])
    args.insert(-1, cmd[0][3] != "no")

    # Add knots.
    args.append([int(x) for x in cmd[1][1:]])
    args.append(int(cmd[1][0]))

    # Add CVs.
    args.append(int(cmd[2][0]))
    args.extend([[float(y) for y in x] for x in cmd[3:]])

    return args


def set_cached(curve, value):
    # type: (str, list[int | bool | list[float]]) -> None
    """Set the value of cached plug.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> curve = cmds.createNode("nurbsCurve")
        >>> points = [[-5, 0, 0], [0, 5, 0], [5, 0, 0]]
        >>> data = [1, 2, 0, False, 3, [0, 1, 2], 3, 3] + points
        >>> set_cached(curve, data)

    Arguments:
        curve (str): The name of the node on which the data should be applied.
        value (list): The curve data that will be apply on the node.
    """
    cmds.setAttr(curve + ".cached", *value, type="nurbsCurve")


def from_points(points, name="curve", degree=3, close=False, method="cv"):
    # type: (list[tuple[float, float, float]], str, int, bool, str) -> str
    """Create a curve from the given points.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> from_points( [(-5, 0, 0), (0, 5, 0), (5, 0, 0)], method="ep")
        'curve'

    Arguments:
        points (list): The points from which the curve will be generated.
        name (str): The name to give to the curve.
        degree (int): The degree of the curve.
        close (bool): Should the curve be build closed?
        method (str): The method used to generate the curve.

    Returns:
        str: The name of the created curve.
    """
    flags = {}  # type: dict[str, Any]
    flags["point"] = points
    flags["degree"] = degree if method == "cv" else 1
    if close:
        flags["point"].extend(points[:degree])
        flags["periodic"] = True
        flags["knot"] = list(range(len(flags["point"]) + flags["degree"] - 1))
        return flags["knot"]
    curve = cmds.curve(**flags)
    curve = cmds.rename(curve, name)

    if method == "ep":
        shape = cmds.listRelatives(curve, shapes=True)[0]
        spline = cmds.createNode("nurbsCurve", parent=curve, name=shape)
        fit = cmds.createNode("fitBspline", name=curve + "_fitBspline")
        cmds.connectAttr(shape + ".worldSpace[0]", fit + ".inputCurve")
        cmds.connectAttr(fit + ".outputCurve", spline + ".create")
        cmds.delete(spline, constructionHistory=True)
        cmds.delete(shape)
        cmds.rename(spline, shape)

    return curve


def from_transforms(
    nodes,
    name="curve",
    degree=3,
    close=False,
    method="cv",
    attach=False,
):
    # type: (str, str, int, bool, str, bool) -> str
    """Create a curve with each point at the position of a transform node.

    If the ``attach`` parameter is set to ``True``, each point of the created
    curve will be driven by the node that gave it its position.

    Its possible to choose between ``ep`` and ``cp`` point to generate the
    curve using the ``method`` parameter. For an ``ep`` curve, the ``degree``
    parameter will be ignored.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.createNode("transform")
        >>> b = cmds.createNode("transform")
        >>> c = cmds.createNode("transform")
        >>> cmds.setAttr(b + ".translate", 5, 10, 0)
        >>> cmds.setAttr(c + ".translate", 10, 0, 0)
        >>> from_transforms(
        ...     (a, b, c),
        ...     degree=1,
        ...     close=True,
        ...     attach=True,
        ...     method="ep"
        ... )
        'curve'

    Arguments:
        nodes (list): The nodes from which the curve will be created.
        name (str): The name of the curve.
        degree (int): The degree of the curve.
        close (bool): Specify if the curve is closed or not.
        method (str): The type of points used to generate the curve.
        attach (bool): Constraint the given nodes to each cvs.

    Returns:
        str: The name of the curve.
    """
    flags = {}  # type: dict[str, Any]
    flags["query"] = True
    flags["translation"] = True
    flags["worldSpace"] = True
    point = [cmds.xform(x, **flags) for x in nodes]

    flags.clear()
    flags["point"] = point
    flags["degree"] = degree
    if close:
        flags["point"].extend(point[:degree])
        flags["periodic"] = True
        flags["knot"] = list(range(len(point) + degree - 1))
    if method == "ep":
        flags["degree"] = 1

    curve = cmds.curve(**flags)
    curve = cmds.rename(curve, name)

    if method == "ep":
        shape = cmds.listRelatives(curve, shapes=True)[0]
        spline = cmds.createNode("nurbsCurve", parent=curve, name=shape)
        fit = cmds.createNode("fitBspline", name=curve + "_fitBspline")
        cmds.connectAttr(shape + ".worldSpace[0]", fit + ".inputCurve")
        cmds.connectAttr(fit + ".outputCurve", spline + ".create")

        if attach:
            cmds.setAttr(shape + ".visibility", False)
        else:
            cmds.delete(spline, constructionHistory=True)
            cmds.delete(shape)
            cmds.rename(spline, shape)

    if not attach:
        return curve
    for index, node in enumerate(nodes):
        name = node + "_decomposeMatrix"
        decompose = cmds.createNode("decomposeMatrix", name=name)
        cmds.connectAttr(node + ".worldMatrix[0]", decompose + ".inputMatrix")
        cmds.connectAttr(
            decompose + ".outputTranslate",
            "{}.cv[{}]".format(curve, index),
        )

    return curve


def replace(old, new):
    # type: (str, str) -> None
    """Replace the shape of the new curve by the one on the old curve.

    Arguments:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.curve(
        ...     point=[(-5, 0, 0), (0, 5, 0), (5, 0, 0)],
        ...     degree=1,
        ... )
        >>> b = cmds.curve(
        ...     point=[(-10, 0, 0), (0, 10, 0), (10, 0, 0)],
        ...     degree=1,
        ... )
        >>> replace(a, b)
    """
    set_cached(new, get_cached(old))


def transform(
    curve,  # type: str
    translate=(0, 0, 0),  # type: tuple[float, float, float]
    rotate=(0, 0, 0),  # type: tuple[float, float, float]
    scale=(1, 1, 1),  # type: tuple[float, float, float]
    space="object",  # type: str
):  # type: (...) -> None
    """Apply transformation on the shape of the given curve.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> curve = cmds.circle()[0]
        >>> transform(
        ...     curve,
        ...     translate=(2, 0, 0),
        ...     rotate=(0, 90, 0),
        ...     scale=(1, 1, 2),
        ... )

    Arguments:
        curve: The curve which contains the shape to transform.
        translate: The translation to apply on the shape.
        rotate: The rotation to apply on the shape.
        scale: The scale to apply on the shape.
        space: The space on which the transformation should be applied.
    """
    flags = {}
    flags["relative"] = True
    flags[space + "Space"] = True

    cvs = curve + ".cv[*]"
    if translate != (0, 0, 0):
        cmds.move(translate[0], translate[1], translate[2], cvs, **flags)
    if rotate != (0, 0, 0):
        cmds.rotate(rotate[0], rotate[1], rotate[2], cvs, **flags)
    if scale != (1, 1, 1):
        cmds.scale(scale[0], scale[1], scale[2], cvs, **flags)
