"""Connection utilities."""
import logging
from typing import List, Optional, cast

from maya import cmds
from maya.api import OpenMaya

__all__ = ["double_operation", "matrix_to_srt", "disconnect", "find_related"]

LOG = logging.getLogger(__name__)


def double_operation(plug, operator="*", value=1):
    # type: (str, str, float) -> str
    """Add a simple double operator to the given plug.

    The suported value fo the operator parameter are: ``+`` (add),
    ``-`` (minus), ``*`` (multiply), ``/`` (divide).

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform", name="A")
        >>> double_operation(node + ".translateX", operator="+")
        'A_operation.output'

    Arguments:
        plug: The source plug on which the operation will be based.
        operator: The operator type that should be used.
        value: The second value that will be used for the operation.

    Returns:
        The new plug which contain the result of the operation.

    Raises:
        ValueError: An invalid operator as been specified.
    """
    if operator == "*":
        node_type = "multDoubleLinear"
    elif operator == "/":
        node_type = "multDoubleLinear"
        value = 1 / value
    elif operator == "+":
        node_type = "addDoubleLinear"
    elif operator == "-":
        node_type = "addDoubleLinear"
        value = -value
    else:
        raise ValueError("Invalid operation '{}'.".format(operator))

    node = plug.split(".")[0]
    node = cast(str, cmds.createNode(node_type, name=node + "_operation"))
    cmds.connectAttr(plug, node + ".input1")
    cmds.setAttr(node + ".input2", value)
    return node + ".output"


def matrix_to_srt(plug, transform, destinations=None):
    # type: (str, str, Optional[List[str]]) -> str
    """Connect a matrix plug to scale/rotate/translate attributes.

    The ``destinations`` parameter accepts a list of strings which represent
    each plug to which the matrix attribute will be connected. ``translate``,
    ``rotate``, ``scale`` and their single axis versions are accepted on both
    long and short name forms.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> mult = cmds.createNode("multMatrix")
        >>> matrix_to_srt(mult + ".matrixSum", node)
        'multMatrix1_decomposeMatrix'

    Arguments:
        plug: The matrix plud to decompose.
        transform: The name of the transform that recieve the matrix.
        destinations: The name of the attributes on which the matrix will be
            connected to.

    Returns:
        The name of the decomposeMatrix node use.
    """
    name = plug.split(".", 1)[0] + "_decomposeMatrix"
    decompose = cast(str, cmds.createNode("decomposeMatrix", name=name))
    cmds.connectAttr(plug, decompose + ".inputMatrix")
    for attribute in destinations or (x + y for x in "srt" for y in "xyz"):
        dst = "{}.{}".format(transform, attribute)
        attribute = cmds.attributeName(dst, short=True)
        cmds.connectAttr("{}.o{}".format(decompose, attribute), dst)
    return decompose


def disconnect(node, attributes=None, source=False, destination=False):
    # type: (str, Optional[List[str]], bool, bool) -> None
    """Disconnect the connection of the given node/attributes.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.createNode("transform")
        >>> b = cmds.createNode("transform")
        >>> _ = cmds.connectAttr(a + ".translateX", a + ".translateY")
        >>> _ = cmds.connectAttr(b + ".translateX", a + ".translateZ")
        >>> disconnect(a, source=True, destination=True)

    Arguments:
        node: The name of the node to disconnect.
        attributes: Filter the attributes that should be disconnected.
        source: Disconnect the source (input) connections.
        destination: Disconnect the destination (output) connections.
    """
    for attribute in attributes or cmds.listAttr(connectable=True) or []:
        plug = "{}.{}".format(node, attribute)

        if not cmds.objExists(plug):
            continue

        if source:
            sources = cmds.listConnections(
                plug,
                source=True,
                destination=False,
                plugs=True,
            )
            for each in sources or []:
                cmds.disconnectAttr(each, plug)

        if destination:
            destinations = cmds.listConnections(
                plug,
                source=False,
                destination=True,
                plugs=True,
            )
            for each in destinations or []:
                cmds.disconnectAttr(plug, each)


def find_related(root, node_type, stream="history"):
    # type: (str, str, str) -> Optional[str]
    """Find a node related to the root.

    The function will search for a node in the specified direction (stream).
    The accepted values are ``history`` and ``future``.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> geo = cmds.polySphere()[0]
        >>> shape = cmds.listRelatives(geo, shapes=True)[0]
        >>> _ = cmds.cluster(geo)
        >>> find_related(shape, "cluster")
        'cluster1'
        >>> find_related(shape, "skinCluster") is None
        True

    Arguments:
        root: The node from which the search will be based.
        node_type: The type of the node to find.
        stream: The direction in which the search will be performed.

    Returns:
        The name of the first node found. If no node matches the parameters,
        returns ``None``.
    """

    sel = OpenMaya.MSelectionList().add(root)
    mit = OpenMaya.MItDependencyGraph(
        sel.getDependNode(0),
        direction={
            "future": OpenMaya.MItDependencyGraph.kDownstream,
            "history": OpenMaya.MItDependencyGraph.kUpstream,
        }.get(stream.lower()),
        traversal=OpenMaya.MItDependencyGraph.kDepthFirst,
        level=OpenMaya.MItDependencyGraph.kPlugLevel,
    )
    while not mit.isDone():
        current = OpenMaya.MFnDependencyNode(mit.currentNode())
        # It would be better to use the maya function set constant directly
        # with the `filter` parameter. The problem is how to get this id from
        # the passed string? If anyone has an idea xD
        # e.g. mesh -> kMesh, skinCluster -> kSkinClusterFilter, etc.
        if current.typeName == node_type:
            return cast(str, current.name())
        mit.next()
    return None
