"""Mesh utilities."""
import logging
import operator
from typing import Optional, Tuple, cast

from maya import cmds
from maya.api import OpenMaya

__all__ = ["reset_vertices", "closest_vertex", "minimal_duplicate"]

LOG = logging.getLogger(__name__)


def reset_vertices(mesh):
    # type: (str) -> None
    """Reset the vertex transforms to 0.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> mesh = cmds.polySphere(constructionHistory=False)[0]
        >>> vtx = mesh + ".vtx[0]"
        >>> cmds.xform(vtx, translation=(0, 10, 0))
        >>> cmds.xform(vtx, query=True, translation=True, worldSpace=True)
        [0.0, 10.0, 0.0]
        >>> reset_vertices(mesh)

    Arguments:
        mesh (str): The name of the mesh to reset.
    """
    for i in range(cmds.polyEvaluate(mesh, vertex=True)):
        cmds.setAttr("{}.pnts[{}].pntx".format(mesh, i), 0)
        cmds.setAttr("{}.pnts[{}].pnty".format(mesh, i), 0)
        cmds.setAttr("{}.pnts[{}].pntz".format(mesh, i), 0)


def closest_vertex(mesh, origin):
    # type: (str, Tuple[float, float, float]) -> Tuple[str, float]
    """Find the closest vertex to a given position.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> mesh = cmds.polyCube()[0]
        >>> closest_vertex(mesh, (0.5, 2, 0.5))
        (3, 1.5)

    Arguments:
        mesh: The name of the mesh on which the vertex will be searched.
        origin: The x, y and z positions of the point to use as the origin.

    Returns:
        The index of the closest vertex as the first index and its distance
        from the origin as the second index.
    """
    sel = OpenMaya.MSelectionList()
    sel.add(mesh)

    space = OpenMaya.MSpace.kWorld
    mfn = OpenMaya.MFnMesh(sel.getDagPath(0).extendToShape())
    point = OpenMaya.MPoint(origin)

    # First find the closest face on the mesh
    face = mfn.getClosestPoint(point, space=space)[1]

    # Then iterates through each vertex of the face to compare their distance
    # with the origin point.
    vertices = []
    for vertex in mfn.getPolygonVertices(face):
        distance = mfn.getPoint(vertex, space=space).distanceTo(point)
        vertices.append((vertex, distance))

    # Finally return the vertex with the smallest distance
    return min(vertices, key=operator.itemgetter(1))


def minimal_duplicate(mesh, name=None):
    # type: (str, Optional[str]) -> str
    """Create a minimal copy of the given mesh.

    Using ``cmds.duplicate()``, everything is duplicated from the source mesh.
    Even garabage data that is not really necessary and potentially dangerous
    to have in the new mesh.

    This function will duplicate the given mesh by only transferring the ID and
    positions of the components from the source mesh.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> src = cmds.polySphere()[0]
        >>> minimal_duplicate(src)
        'pSphere2Shape'

    Arguments:
        mesh: The name of the mesh that should be duplicated.
        name: The name to give to the duplicated mesh.

    Returns:
        The name of the duplicated mesh.
    """
    sel = OpenMaya.MSelectionList()
    sel.add(mesh)
    path = sel.getDagPath(0)  # type: OpenMaya.MDagPath
    path.extendToShape()

    src = OpenMaya.MFnMesh(path)
    dst = OpenMaya.MFnMesh()

    count = []
    connect = []
    for i in range(src.numPolygons):
        count.append(src.polygonVertexCount(i))
        connect.extend(src.getPolygonVertices(i))

    dag = OpenMaya.MDagModifier()
    obj = dag.createNode("transform")
    dag.renameNode(obj, name or mesh)
    dag.doIt()

    dst.create(src.getPoints(), count, connect, parent=obj)
    dst.setName(OpenMaya.MFnTransform(obj).name() + "Shape")

    return cast(str, dst.name())
