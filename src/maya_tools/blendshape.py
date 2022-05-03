"""Blendshape utilities."""
import logging
from typing import Collection, Iterable

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest  # type: ignore

from maya import cmds

__all__ = ["create", "find_next_available_target"]

LOG = logging.getLogger(__name__)


def create(
    base,  # type: str
    targets,  # type: Collection[str]
    weights=0,  # type: Iterable[float] | float
    name="blendShape",  # type: str
    aliases=None,  # type: Iterable[str]
):  # type: (...) -> str
    """Create a new blendshape deformer.

    If a single value is passed to the ``weights`` argument, this value will be
    applied to all the targets.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.polySphere()[0]
        >>> b = cmds.polySphere()[0]
        >>> c = cmds.polySphere()[0]
        >>> create(a, [b, c], aliases=["First", "Second"])
        'blendShape'

    Arguments:
        base: The geometry on which the deformer will be created.
        targets: The geometries that will be connected to the deformer.
        weights: The weights value of each target.
        name: The name of the new blendshape.
        aliases: The alias to give to each target.

    Returns:
        The name of the created blendshape deformer.
    """
    if isinstance(weights, (int, float)):
        weights = [weights] * len(targets)

    deformer = cmds.blendShape(base, name=name)[0]
    iterable = zip_longest(targets, aliases or [], weights)
    for i, (target, alias, weight) in enumerate(iterable):
        cmds.blendShape(
            deformer,
            edit=True,
            target=(base, i, target, 1),
            topologyCheck=False,
        )
        cmds.setAttr("{}.{}".format(deformer, target), weight)
        if alias is not None:
            cmds.aliasAttr(alias, "{}.weight[{}]".format(deformer, i))
    return deformer


def find_next_available_target(deformer):
    # type: (str) -> int
    """Find the next available target in the blendshape deformer.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.polySphere()[0]
        >>> b = cmds.polySphere()[0]
        >>> c = cmds.polySphere()[0]
        >>> bs = cmds.blendShape(a, b, c)[0]
        >>> find_next_available_target(bs)
        2

    Arguments:
        deformer: The name of the blendshape to query.

    Returns:
        The first available target in the blendshape.
    """
    plug = "{}.inputTarget[0].inputTargetGroup[{}]"
    plug += ".inputTargetItem[6000].inputGeomTarget"
    index = 0
    while cmds.listConnections(plug.format(deformer, index), source=True):
        index += 1
    return index
