"""Provide utilities related to colors."""
import logging

import webcolors

from maya import cmds

__all__ = ["INDICES", "index", "name", "rgb", "disable"]

LOG = logging.getLogger(__name__)

INDICES = {
    "no": 0,
    "black": 1,
    "dark-gray": 2,
    "light-gray": 3,
    "dark-red": 4,
    "dark-blue": 5,
    "blue": 6,
    "dark-green": 7,
    "purple": 8,
    "pink": 9,
    "brown": 10,
    "dark-brown": 11,
    "light-red": 12,
    "red": 13,
    "green": 14,
    # "": 15,
    "white": 16,
    "yellow": 17,
    "light-blue": 18,
    "light-green": 19,
    "light-pink": 20,
    "light-brown": 21,
    "light-yellow": 22,
    # "": 23,
    # "": 24,
    # "": 25,
    # "": 26,
    # "": 27,
    # "": 28,
    # "": 29,
    "light-purple": 30,
    # "": 31,
}


def index(node, value=0):
    # type: (str, int) -> None
    """Set the color of a node using the maya index.

    Tip:
        It's possible to query and edit the maya default index color by using
        the ``cmds.colorIndex()`` command.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.circle()[0]
        >>> index(node, 18)
        >>> cmds.getAttr(node + ".overrideColor")
        18
        >>> index(node)
        >>> cmds.getAttr(node + ".overrideColor")
        0

    Arguments:
        node (str): The name of the node on which the color will be applied.
        value (int): The index of the color to apply.

    Raises:
        ValueError: The provided value is not in the valid range.
    """
    cmds.setAttr(node + ".overrideEnabled", True)
    cmds.setAttr(node + ".overrideRGBColors", False)
    cmds.setAttr(node + ".overrideColor", value)


def name(node, value):
    # type: (str, str) -> None
    """Set the RGB values using CSS color names.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.circle()[0]
        >>> name(node, "red")
        >>> cmds.getAttr(node + ".overrideColorRGB")[0]
        (1.0, 0.0, 0.0)

    Arguments:
        node (str): The name of the node on which the color will be appied.
        value (str): The name of the color to apply.
    """
    rgb(node, webcolors.name_to_rgb(value))


def rgb(node, values, rerange=255):
    # type: (str, tuple[float, float, float], int) -> None
    """Set the color of a node using RGB values.

    Caution:
        This function work is a rgb range between 0 and 255. However, maya
        uses an internal range between 0 and 1. It's still possible to work
        with the maya range by setting the ``rerange`` parameter to 1.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.circle()[0]
        >>> rgb(node, (255, 0, 0))
        >>> cmds.getAttr(node + ".overrideColorRGB")[0]
        (1.0, 0.0, 0.0)
        >>> rgb(node, (1, 0, 1), rerange=1)
        >>> cmds.getAttr(node + ".overrideColorRGB")[0]
        (1.0, 0.0, 1.0)

    Arguments:
        node (str): The name of the node on which the color will be appied.
        values (tuple): The RGB values of the color to apply.
        rerange (int): The maximum color value. Usually 1 or 255.
    """
    cmds.setAttr(node + ".overrideEnabled", True)
    cmds.setAttr(node + ".overrideRGBColors", True)
    cmds.setAttr(node + ".overrideColorRGB", *(x / rerange for x in values))


def disable(node):
    """Disable the color override.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> cmds.setAttr(node + ".overrideEnabled", True)
        >>> cmds.setAttr(node + ".overrideColor", 10)
        >>> disable(node)
        >>> cmds.getAttr(node + ".overrideEnabled")
        False
        >>> cmds.getAttr(node + ".overrideColor")
        0

    Arguments:
        node (str): The name of the node on which disable the color override.
    """
    cmds.setAttr(node + ".overrideEnabled", False)
    cmds.setAttr(node + ".overrideRGBColors", False)
    cmds.setAttr(node + ".overrideColor", 0)
    cmds.setAttr(node + ".overrideColorRGB", 0, 0, 0)
