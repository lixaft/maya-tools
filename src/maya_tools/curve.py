"""Curve releated utilities."""
from __future__ import division

import logging
from typing import Any, Dict, List, Tuple, Union, cast

from maya import cmds

import maya_tools.api

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

Vector = Tuple[float, float, float]
Cached = List[Union[int, bool, List[float]]]


def get_points(curve, world=False, method="cv"):
    # type: (str, bool, str) -> List[Vector]
    """Query the position of each control points of a curve.

    The ``method`` parameter controls the type of point used to return
    positions. It accepts either ``ep`` or ``cv`` as a value.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.curve(
        ...     point=[(-5, 0, 0), (0, 5, 0), (5, 0, 0)],
        ...     degree=1,
        ... )
        >>> cmds.setAttr(node + ".translateZ", -2)
        >>> get_points(node, world=True)
        [(-5.0, 0.0, -2.0), (0.0, 5.0, -2.0), (5.0, 0.0, -2.0)]

    Arguments:
        curve: The name of the curve node to query.
        world: Specify on which space the coordinates will be returned.
        method: Which type of points should be queried.

    Returns:
        A two-dimensional array that contains all the positions of the  points
        that compose the curve.
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
    # type: (str) -> Cached
    """Extract the data contained in the .cached attribute.

    This function required a static sha[e (a.k.a no history) in order to
    return any value.

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
        curve: The the curve from which the data should be extracted.

    Returns:
        The cached data as a list.
    """
    plug = maya_tools.api.as_plug(curve + ".cached")
    cmd = [x.strip().split() for x in plug.getSetAttrCmds()[1:-1]]

    # Add base.
    args = []  # type: Cached
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
    # type: (str, Cached) -> None
    """Set the value of cached plug.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> curve = cmds.createNode("nurbsCurve")
        >>> points = [[-5, 0, 0], [0, 5, 0], [5, 0, 0]]
        >>> data = [1, 2, 0, False, 3, [0, 1, 2], 3, 3] + points
        >>> set_cached(curve, data)

    Arguments:
        curve: The name of the node on which the data should be applied.
        value: The curve data that will be apply on the node.
    """
    cmds.setAttr(curve + ".cached", *value, type="nurbsCurve")


def from_points(points, name="curve", degree=3, close=False, method="cv"):
    # type: (List[Vector], str, int, bool, str) -> str
    """Create a curve from the given points.

    The curve can be created using two different method: ``cv``  and ``ep``.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> from_points( [(-5, 0, 0), (0, 5, 0), (5, 0, 0)], method="ep")
        'curve'

    Arguments:
        points: The points from which the curve will be generated.
        name: The name to give to the curve.
        degree: The degree of the curve.
        close: Should the curve be build closed?
        method: The method used to generate the curve.

    Returns:
        The name of the created curve.
    """
    flags = {}  # type: Dict[str, Any]
    flags["point"] = points
    flags["degree"] = degree if method == "cv" else 1
    if close:
        flags["point"].extend(points[:degree])
        flags["periodic"] = True
        flags["knot"] = list(range(len(points) + degree - 1))
    if method == "ep":
        flags["degree"] = 1
    curve = cast(str, cmds.curve(**flags))
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
    # pylint: disable=too-many-arguments
    """Create a curve with each point at the position of a transform node.

    If the ``attach`` parameter is set to ``True``, each point of the created
    curve will be driven by the node that gave it its position.

    Its possible to choose between ``ep`` and ``ep`` point to generate the
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
        nodes: The nodes from which the curve will be created.
        name: The name of the curve.
        degree: The degree of the curve.
        close: Specify if the curve is closed or not.
        method: The type of points used to generate the curve.
        attach: Constraint the given nodes to each cvs.

    Returns:
        The name of the curve.
    """
    flags = {}  # type: Dict[str, Any]
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

    curve = cast(str, cmds.curve(**flags))
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


def replace(source, destination):
    # type: (str, str) -> None
    """Replace the shape of the new curve by the one on the old curve.:

    Examples:
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

    Arguments:
        source: The name of the curve that should be copied.
        destination: The name of the curve on which the source will be copied.
    """
    set_cached(destination, get_cached(source))


def transform(
    curve,  # type: str
    translate=(0, 0, 0),  # type: Vector
    rotate=(0, 0, 0),  # type: Vector
    scale=(1, 1, 1),  # type: Vector
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
