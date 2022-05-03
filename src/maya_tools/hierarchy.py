"""Hierarchy utilities."""
import logging

from maya import cmds
from maya.api import OpenMaya

__all__ = ["make", "tree", "sort"]

LOG = logging.getLogger(__name__)


def make(path, node="transform"):
    # type: (str, str) -> str
    """Create a full path in maya outliner.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> make("A|B|C")
        'C'
        >>> cmds.listRelatives("C", parent=True)[0]
        'B'
        >>> cmds.listRelatives("B", parent=True)[0]
        'A'

    Arguments:
        path (str): The full path to create.
        node (str): The type of node to create for the path.

    Returns:
        str: The name of the tail of the path.
    """
    nodes = path.split("|")
    for i, each in enumerate(nodes):
        if not cmds.objExists(each):
            cmds.createNode(node, name=each)
        if i > 0:
            cmds.parent(each, nodes[i - 1])
    return nodes[-1]


def tree(root, include_root=False):
    # type: (str, bool) -> dict[str, dict]
    """Get the node tree from the specified root node.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.createNode("transform", name="A")
        >>> b = cmds.createNode("transform", name="B", parent=a)
        >>> c = cmds.createNode("transform", name="C", parent=a)
        >>> expected = {
        ...     "A": {
        ...         "B": {},
        ...         "C": {},
        ...     }
        ... }
        >>> tree(a, include_root=True) == expected
        True

    Arguments:
        root (str): The name of the node from which the search will start.
        include_root(bool): Include the root node in the returned dict.

    Returns:
        dict: A dictionary that contains all descendants of the root node.
    """
    tree_dict = {}
    for child in cmds.listRelatives(root, children=True) or []:
        tree_dict[child] = tree(child)
    if include_root:
        return {root: tree_dict}
    return tree_dict


def sort(root=None, recursive=False):
    """Sort the children of the provided root.

    If no root node is specified, reorder the top level nodes.

    Arguments:
        root (str): The node from which their children will be sorted.
        recursive (bool): Recurssively sort all descendants of the root.
    """
    if root is None:
        nodes = cmds.ls(assemblies=True)
    else:
        nodes = cmds.listRelatives(root, children=True) or []
    for child in reversed(sorted(nodes)):
        cmds.reorder(child, front=True)
        if recursive:
            sort(child, recursive=True)


def safe_descendants(node, path=False):
    """Safe iteration over the descendants of the given node.

    Arguments:
        node (str): The name of the root node.
        path (bool): Return the full path instead of just the node name.

    Yeilds:
        str: The current node name or path.
    """
    sel = OpenMaya.MSelectionList()
    sel.add(node)
    obj = sel.getDependNode(0)
    iterator = OpenMaya.MItDag()
    iterator.reset(obj)
    iterator.next()
    while not iterator.isDone():
        if path:
            yield iterator.fullPathName()
        else:
            yield iterator.partialPathName()
        iterator.next()
