"""Provide utilities related to skinclusters."""
import logging

from maya import cmds, mel

__all__ = [
    "create",
    "find_influences",
    "add_influences",
    "remove_influences",
    "remove_unused_influences",
]

LOG = logging.getLogger(__name__)


def create(node, influences, method="blend"):
    # type: (str, list[str], str) -> str | None
    """Create and attach a skincluster to the specified node.

    The ``method`` parameter defines the algorithm used to get the position of
    each component of the deformed object. The value can be either ``linear``,
    ``dualQuaternion`` or ``blend``.

    If the target node already have a skincluster attached, the function will
    just add the missing influences to the existing deformer.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> msh, _ = cmds.polyCube(name="cube")
        >>> joints = [cmds.createNode("joint") for _ in range(3)]
        >>> create(msh, joints)
        'cube_skinCluster'

    Arguments:
        node (str): The node on which creates the skincluster.
        influences (list, optional): The influence objects that will deform
            the skincluster.
        method (str): The binded method that will be used to deform the mesh.

    Returns:
        str: The name of the created skincluster.

    Raises:
        ValueError: The specified method id not recognized.
    """
    try:
        method_index = {"linear": 0, "dualQuaternion": 1, "blend": 2}[method]
    except KeyError:
        raise ValueError("The method '{}' is not valid.".format(method))

    skincluster = mel.eval("findRelatedSkinCluster {}".format(node))
    if not skincluster:
        skincluster = cmds.skinCluster(
            node,
            influences,
            name=node + "_skinCluster",
            skinMethod=method_index,
            toSelectedBones=True,
            removeUnusedInfluence=False,
        )[0]
    else:
        current = cmds.skinCluster(skincluster, query=True, influence=True)
        delta = set(influences) - set(current)
        cmds.skinCluster(skincluster, edit=True, addInfluence=delta)

    return skincluster


def find_influences(node, weighted=True, unused=True):
    """Get the associated influence objects associated to a skincluster.

    Example:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> msh, _ = cmds.polyCube()
        >>> a = cmds.createNode("joint", name="A")
        >>> b = cmds.createNode("joint", name="B")
        >>> skc = cmds.skinCluster(msh, a, b)[0]
        >>> find_influences(msh)
        ['A', 'B']

        Filter the weighted influences.

        >>> cmds.skinPercent(
        ...     skc,
        ...     msh + ".vtx[*]",
        ...     transformValue=[(a, 1), (b, 0)],
        ... )
        >>> find_influences(msh, weighted=True, unused=False)
        ['A']
        >>> find_influences(msh, weighted=False, unused=True)
        ['B']

    Arguments:
        node (str): The node on which query the influence objects.
        weighted (bool): Include the influence objects with non-zero weights.
        unused (bool): Include the influence objects with zero weights.

    Returns:
        list: An array containing the influence objects.
    """
    skc = mel.eval("findRelatedSkinCluster {}".format(node))
    all_ = cmds.skinCluster(skc, query=True, influence=True)
    if unused and weighted:
        return all_
    weighted_ = cmds.skinCluster(node, query=True, weightedInfluence=True)
    if weighted:
        return weighted_
    return list(set(all_) - set(weighted_))


def add_influences(node, influences):
    """Add influences to an existing skincluster.

    Note:
        If the specified node does not have a skincluster attached to it,
        simply log an error without doing anything else.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> msh = cmds.polyCube()[0]
        >>> a = cmds.createNode("joint", name="A")
        >>> b = cmds.createNode("joint", name="B")
        >>> _ = cmds.skinCluster(msh, a)
        >>> cmds.skinCluster(msh, query=True, influence=True)
        ['A']
        >>> add_influences(msh, [b])
        >>> cmds.skinCluster(msh, query=True, influence=True)
        ['A', 'B']

    Arguments:
        node (str): The deformed node on which the skincluster is attached.
        influences (list): The influences nodes to add to the skincluster.
    """
    skincluster = mel.eval("findRelatedSkinCluster {}".format(node))
    if not skincluster:
        LOG.error("No skincluster found under the node '%s'.", node)
        return
    current = cmds.skinCluster(skincluster, query=True, influence=True)
    delta = set(influences) - set(current)
    cmds.skinCluster(skincluster, edit=True, addInfluence=delta)


def remove_influences(node, influences):
    """Remove influences to an existing skincluster.

    Note:
        If the specified node does not have a skincluster attached to it,
        simply log an error without doing anything else.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> msh, _ = cmds.polyCube()
        >>> a = cmds.createNode("joint", name="A")
        >>> b = cmds.createNode("joint", name="B")
        >>> _ = cmds.skinCluster(msh, a, b)
        >>> cmds.skinCluster(msh, query=True, influence=True)
        ['A', 'B']
        >>> remove_influences(msh, [b])
        >>> cmds.skinCluster(msh, query=True, influence=True)
        ['A']

    Arguments:
        node (str): The deformed node on which the skincluster is attached.
        influences (list): The influence nodes to add to the skincluster.

    Raises:
        RuntimeError: No skincluster attached on the node.
    """
    skincluster = mel.eval("findRelatedSkinCluster {}".format(node))
    if not skincluster:
        msg = "No skincluster found under the node '{}'."
        raise RuntimeError(msg.format(node))
    inf = set(influences) & set(find_influences(node))
    cmds.skinCluster(skincluster, edit=True, removeInfluence=list(inf))


def remove_unused_influences(node):
    """Remove the unused influences using the :func:`remove` function.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> msh, _ = cmds.polyCube()
        >>> a = cmds.createNode("joint", name="A")
        >>> b = cmds.createNode("joint", name="B")
        >>> skc = cmds.skinCluster(msh, a, b)[0]
        >>> cmds.skinPercent(
        ...     skc,
        ...     msh + ".vtx[*]",
        ...     transformValue=[(a, 1), (b, 0)],
        ... )
        >>> remove_unused_influences(msh)
        >>> cmds.skinCluster(msh, query=True, influence=True)
        ['A']

    Arguments:
        node (str): The deformed node on which the skincluster is attached.
    """
    remove_influences(node, find_influences(node, weighted=False, unused=True))
