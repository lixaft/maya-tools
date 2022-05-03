"""Provide utilities related to deformers."""
import logging

from maya import cmds

__all__ = ["find", "find_set"]

LOG = logging.getLogger(__name__)


def find(node, type=None):
    # pylint: disable=redefined-builtin
    """Find all the deformers associated to the node.

    Arguments:
        node (str): The name of node on which find the deformers.
        sets (bool): Return the deformer sets instead of the deformers.
        type (str): Filter the type of the returned deformers.

    Retruns:
        list: An array that will contains all the deofmers of the shape.
    """
    result = []
    for deformer in cmds.findDeformers(node):
        if type is not None and cmds.nodeType(deformer) != type:
            continue
        else:
            result.append(deformer)
    return result


def find_set(node):
    """Find the set of a deformer node.

    Arguments:
        node (str): The name of the node on which the set will be retrived.

    Returns:
        str: The name of the deformer set.
    """
    for each in cmds.listHistory(node, future=True):
        if "geometryFilter" not in cmds.nodeType(each, inherited=True):
            continue
        sets = cmds.listConnections(
            each + ".message",
            type="objectSet",
            exactType=True,
        )
        return (sets or [None])[0]
