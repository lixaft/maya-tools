"""Provide utilities related to deformers."""
import logging
from typing import List, Optional

from maya import cmds

__all__ = ["find", "find_set"]

LOG = logging.getLogger(__name__)


def find(node, type=None):
    # type: (str, Optional[str]) -> List[str]
    # pylint: disable=redefined-builtin
    """Find all the deformers associated to the node.

    Arguments:
        node: The name of node on which find the deformers.
        sets: Return the deformer sets instead of the deformers.
        type: Filter the type of the returned deformers.

    Retruns:
        An array that will contains all the deofmers of the shape.
    """
    result = []
    for deformer in cmds.findDeformers(node):
        if type is not None and cmds.nodeType(deformer) != type:
            continue
        result.append(deformer)
    return result


def find_set(node):
    # type: (str) -> Optional[str]
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
        )  # type: Optional[List[str]]
        if sets:
            return sets[0]
    return None
