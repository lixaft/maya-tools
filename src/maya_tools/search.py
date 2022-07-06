"""Common utilities to search nodes in the current scene."""
import itertools
import logging
import re
from typing import Optional, Sequence

from maya import cmds

LOG = logging.getLogger(__name__)

__all__ = ["regex"]


def regex(expression):
    """Find nodes based on regular expression.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> list(regex(r".+Shape$"))
        ['perspShape', 'topShape', 'frontShape', 'sideShape']

    Arguments:
        expression (str): The regex that should match the node name to search.

    Yield:
        str: The name of the node that match the expression.
    """
    regex_ = re.compile(expression)
    for each in cmds.ls():
        if regex_.match(each):
            yield each


def mirror(node, patterns=("L_:R_", "l_:r_")):
    # type: (str, Sequence[str]) -> Optional[str]
    """Find the opposite of the specified node.

    The function will search for a pattern in the given node name. If a match
    is found, the opposite pattern will be used to check if the corresponding
    node exists in the scene.

    A pattern consists of a string divided into two parts separated by the
    character `:` (the order does not matter). One is the pattern that should
    be searched for in the given node and the other will be the one with which
    the opposite will be searched.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> _ =cmds.createNode("transform", name="L_a")
        >>> _ = cmds.createNode("transform", name="R_a")
        >>> mirror("L_a")
        'R_a'

    Arguments:
        node: The node for which the opposite will be searched.
        pattern:

    Returns:
        The name of the opposite node or None in the case where nothing as
        been found.
    """
    for pattern in patterns:
        right, left = pattern.split(":")
        for current, opposite in itertools.permutations((left, right)):
            if current not in node:
                continue

            opposite_node = node.replace(current, opposite)
            return opposite_node if cmds.objExists(opposite_node) else None
    return None
