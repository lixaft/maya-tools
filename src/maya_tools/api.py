"""Maya api utilities."""
import logging

from maya import cmds
from maya.api import OpenMaya

__all__ = [
    "as_selection",
    "as_object",
    "as_dg",
    "as_dag",
    "as_path",
    "as_plug",
    "as_attribute",
]

LOG = logging.getLogger(__name__)


def as_selection(name):
    # type: (str) -> OpenMaya.MSelectionList
    """Return the given name inside an MSelectionList.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> as_selection("persp")
        <OpenMaya.MSelectionList object at 0x...>

    Arguments:
        name (str): The name of the object to convert.

    Returns:
        OpenMaya.MSelectionList: The converted instance of the name.
    """
    sel = OpenMaya.MSelectionList()
    sel.add(name)
    return sel


def as_object(name):
    # type: (str) -> OpenMaya.MObject
    """Get the MObject associated to the given name.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> as_object("persp")
        <OpenMaya.MObject object at 0x...>

    Arguments:
        name (str): The name of the object to convert.

    Returns:
        OpenMaya.MObject: The converted instance of the name.
    """
    return as_selection(name).getDependNode(0)


def as_dg(name):
    # type: (str) -> OpenMaya.MFnDependencyNode
    """Get the MFnDependencyNode associated to the given name.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> as_dg("persp.translateX")
        <OpenMaya.MFnDependencyNode object at 0x...>

    Arguments:
        name (str): The name of the object to convert.

    Returns:
        OpenMaya.MFnDependencyNode: The converted instance of the name.
    """
    return OpenMaya.MFnDependencyNode(as_object(name))


def as_dag(name):
    # type: (str) -> OpenMaya.MFnDagNode
    """Get the MFnDagNode associated to the given name.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> as_dag("persp.translateX")
        <OpenMaya.MFnDagNode object at 0x...>

    Arguments:
        name (str): The name of the object to convert.

    Returns:
        OpenMaya.MFnDagNode: The converted instance of the name.
    """
    return OpenMaya.MFnDagNode(as_object(name))


def as_path(name):
    # type: (str) -> OpenMaya.MDagPath
    """Get the MDagPath associated to the given name.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> as_path("persp")
        <OpenMaya.MDagPath object at 0x...>

    Arguments:
        name (str): The name of the object to convert.

    Returns:
        OpenMaya.MDagPath: The converted instance of the name.
    """
    return as_selection(name).getDagPath(0)


def as_plug(name):
    # type: (str) -> OpenMaya.MPlug
    """Get the MPlug associated to the given name.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> as_plug("persp.translateX")
        <OpenMaya.MPlug object at 0x...>

    Arguments:
        name (str): The name of the object to convert.

    Returns:
        OpenMaya.MPlug: The converted instance of the name.
    """
    return as_selection(name).getPlug(0)


def as_attribute(name):
    # type: (str) -> OpenMaya.MFnAttribute
    """Get the MFnAttribute associated to the given name.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> as_attribute("persp.translateX")
        <OpenMaya.MFnAttribute object at 0x...>

    Arguments:
        name (str): The name of the object to convert.

    Returns:
        OpenMaya.MFnAttribute: The converted instance of the name.
    """
    return OpenMaya.MFnAttribute(as_plug(name).attribute())


def as_mesh(name):
    # type: (str) -> OpenMaya.MFnMesh
    """Get the MFnMesh associated to the given name.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> as_mesh(cmds.polySphere()[0])
        <OpenMaya.MFnMesh object at 0x...>

    Arguments:
        name (str): The name of the object to convert.

    Returns:
        OpenMaya.MFnMesh: The converted instance of the name.
    """
    return OpenMaya.MFnMesh(as_path(name).extendToShape().node())


def get_matrix(name):
    # type: (str) -> OpenMaya.MMatrix
    """Get the MMatrix associated to the given name.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> get_matrix(cmds.polySphere()[0])
        maya.api.OpenMaya.MMatrix(...)

    Arguments:
        name: The name of the object to query.

    Returns:
        The MMatrix instance where the given node is located.
    """
    matrix = cmds.xform(name, query=True, matrix=True, worldSpace=True)
    return OpenMaya.MMatrix(matrix)
