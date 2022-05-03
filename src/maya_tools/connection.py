"""Connection utilities."""
import logging

from maya import cmds
from maya.api import OpenMaya

__all__ = ["matrix_to_srt", "disconnect", "find_related"]

LOG = logging.getLogger(__name__)


def matrix_to_srt(plug, transform, destinations=None):
    # type: (str, str, list[str] | None) -> str
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
        plug (str): The matrix plud to decompose.
        transform (str): The name of the transform that recieve the matrix.
        destinations (list, optional): The name of the attributes on which the
            matrix will be connected to.

    Returns:
        str: The name of the decomposeMatrix node use.
    """
    name = plug.split(".", 1)[0] + "_decomposeMatrix"
    decompose = cmds.createNode("decomposeMatrix", name=name)
    cmds.connectAttr(plug, decompose + ".inputMatrix")
    for attribute in destinations or (x + y for x in "srt" for y in "xyz"):
        dst = "{}.{}".format(transform, attribute)
        attribute = cmds.attributeName(dst, short=True)
        cmds.connectAttr("{}.o{}".format(decompose, attribute), dst)
    return decompose


def disconnect(node, attributes=None, source=False, destination=False):
    # type: (str, list[str] | None, bool, bool) -> None
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
        node (str): The name of the node to disconnect.
        attributes (list, optional): Filter the attributes that should be
            disconnected.
        source (bool): Disconnect the source (input) connections.
        destination (bool): Disconnect the destination (output) connections.
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
    # type: (str, str, str) -> str | None
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
        root (str): The node from which the search will be based.
        node_type (str): The type of the node to find.
        stream (str): The direction in which the search will be performed.

    Returns:
        str: The name of the first node found. If no node matches the
            parameters, returns ``None``.
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
            return current.name()
        mit.next()
    return None
