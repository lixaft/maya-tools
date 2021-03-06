"""Connection related utilities."""
import codecs
import contextlib
import json
import logging
import re
from typing import Any, Dict, Generator, List, Optional, Sequence, Union

from maya import cmds, mel
from maya.api import OpenMaya

import maya_tools.io

__all__ = [
    "TRANSLATE",
    "ROTATE",
    "SCALE",
    "SHEAR",
    "SRT",
    "SHORT_SRT",
    "add_separator",
    "copy",
    "reset",
    "restore",
    "unlock",
    "find_used_indices",
    "find_next_index",
    "delete_user_defined",
    "move",
    "write_data",
    "read_data",
]

LOG = logging.getLogger(__name__)

TRANSLATE = ("translateX", "translateY", "translateZ")
ROTATE = ("rotateX", "rotateY", "rotateZ")
SCALE = ("scaleX", "scaleY", "scaleZ")
SHEAR = ("shearX", "shearY", "shearZ")

SRT = SCALE + ROTATE + TRANSLATE
SHORT_SRT = tuple(x + y for x in "srt" for y in "xyz")


def add_separator(node, right=None, left=None, name="separator{index:02}"):
    # type: (str, Optional[str], Optional[str], str) -> str
    """Add a dummy attribute in the channel box to create a visual separator.

    On the node, an enum attribute will be added to construct the separator.

    The name of the dummy attribute will be automatically generated by the
    function to have an unique name. By default, the attribute should look like
    something similar to: ``separator00``, ``separator01``, ``separator02``...

    The ``name`` argument can be used to modify the generated name. To make the
    attribute name unique, the provided string must at least contain the
    sub-string ``{index}``, which will be substituted with an unique index
    using the ``str.format`` method.

    Some labels can be added to the separator to help categorise attributes.
    The niceName of the attribute is affected by the ``right`` argument,
    whereas the enumName is affected by the ``left`` argument.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform", name="test")
        >>> add_separator(node)
        'test.separator00'
        >>> add_separator(node)
        'test.separator01'

    Arguments:
        node (str): The node on which the separator should be added.
        right (str, optional): The label displayed on the right side of the
            separator attribute.
        left (str, optional): The label displayed on the left side of the
            separator attribute.
        name (str): The name that will be given to the separator attribute.

    Returns:
        str: The name of the plug corresponding to the created separator.

    Raises:
        ValueError: The given value of ``name`` argument does not contain the
        sub-string ``{index}``.
    """
    # Check that the specified attribute name is valid.
    # I'm wondering if there isn't a better way to check this?
    if "{index" not in name:
        msg = "The name must contain '{index}' to substitue the index."
        raise ValueError(msg)

    # Generate an unique attribute name.
    index = 0
    base_name = "{{}}.{}".format(name)
    plug = base_name.format(node, index=index)
    while cmds.objExists(plug):
        index += 1
        plug = base_name.format(node, index=index)

    # Create the attribute.
    cmds.addAttr(
        node,
        longName=plug.split(".", 1)[-1],
        niceName=right or " ",
        attributeType="enum",
        enumName=left or " ",
    )
    cmds.setAttr(plug, channelBox=True)
    return plug


def copy(source, destination, values=False, attributes=None, fatal=False):
    # type: (str, str, bool, Optional[List[str]], bool) -> List[str]
    """Copy the attribute(s) from the source node to the destination node.

    If no attributes are specified, all the user-defined attributes of the
    source node will be copied to the destination node.

        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> a = cmds.createNode("transform")
        >>> b = cmds.createNode("transform")
        >>> cmds.addAttr(a, longName="test")
        >>> cmds.objExists(b + ".test")
        False
        >>> copy(a, b)
        ['test']
        >>> cmds.objExists(b + ".test")
        True

    If the attribute to copy already exists on the destination node, it will
    simply be ignored by the process, unless ``fatal=True`` is specified, which
    means that an error will be raised instead.

    By default, the current values of the attributes will not be copied to the
    newly created attribute on the destination node (only the default values
    will be as they are part of the attribute creation). To have these values
    copied, use ``values=True``.

        >>> a = cmds.createNode("transform")
        >>> b = cmds.createNode("transform")
        >>> cmds.addAttr(a, longName="test", defaultValue=1.0)
        >>> cmds.setAttr(a + ".test", 2.0)
        >>> copy(a, b)
        ['test']
        >>> cmds.getAttr(b + ".test")
        1.0
        >>> cmds.deleteAttr(b, attribute="test")
        >>> copy(a, b, values=True)
        ['test']
        >>> cmds.getAttr(b + ".test")
        2.0

    Multiple, compound attributes and their nested versions are also supported.
    By specifying the parent attribute, all related child attributes will aslo
    be copied to the destination node.

        >>> a = cmds.createNode("transform")
        >>> b = cmds.createNode("transform")
        >>> cmds.addAttr(a, longName="test", at="compound", numberOfChildren=2)
        >>> cmds.addAttr(a, longName="testA", parent="test")
        >>> cmds.addAttr(a, longName="testB", parent="test")
        >>> copy(a, b, attributes=["test"])
        ['test', 'testA', 'testB']
        >>> cmds.objExists(b + ".testA")
        True
        >>> cmds.objExists(b + ".testB")
        True

    Arguments:
        source (str): The node from which the attributes will be copied.
        destination (str): The node on which the attributes will be created.
        values (bool): Copy the current values to the destination attributes.
        attributes (list, optional): Filter the attributes to copy.
        fatal (bool): Raise an error when a attribute already exists on the
            destination node.

    Returns:
        list: The name of the attributes that has been copied.

        The returned attribute do not contain any node names, which means they
        can be easily use with different nodes.

    Raises:
        AttributeError: An attribute already exists on the destination node.
    """
    copied_attributes = []
    attributes = attributes or cmds.listAttr(source, userDefined=True) or []

    for attribute in attributes:
        src_plug = "{}.{}".format(source, attribute)
        dst_plug = "{}.{}".format(destination, attribute)

        # `MFnCompoundAttribute.getAddAttrCmds` already handles the creation of
        # all the children of a compound attribute for us.
        parent = cmds.attributeQuery(attribute, node=source, listParent=True)
        if parent:
            continue

        # Check if the destination attribute does not already exists.
        exists = cmds.objExists(dst_plug)
        if exists and fatal:
            msg = "The plug '{}' already exists.".format(dst_plug)
            raise AttributeError(msg)

        # Get the MFnAttribute instance of the source plug.
        sel = OpenMaya.MSelectionList()
        sel.add(src_plug)
        plug = sel.getPlug(0)

        # Create the attribute if it doesn't already exist.
        if not exists:
            obj = plug.attribute()

            # Get the mel command(s) needed to recreate the attribute(s).
            commands = []
            if obj.hasFn(OpenMaya.MFn.kCompoundAttribute):
                mfn = OpenMaya.MFnCompoundAttribute(obj)
                commands.extend(mfn.getAddAttrCmds(longNames=True))
            else:
                mfn = OpenMaya.MFnAttribute(obj)
                commands.append(mfn.getAddAttrCmd(longFlags=True))

            # Recreate the attribute in the destination node.
            # NOTE: Remove the first indent (why Maya... xD) and the last ';'.
            commands = ["{} {}".format(x[1:-1], destination) for x in commands]
            cmd = ";".join(commands)
            LOG.debug("Evaluate mel command: %s;", cmd)
            mel.eval(cmd)

            # Register the created attributes.
            copied_attributes.extend(re.findall(r'-longName\s"(\w+)"', cmd))

        # Finally copy the current source value to the destination attribute.
        if values:
            commands = plug.getSetAttrCmds(useLongNames=True)
            commands = ["{} {}".format(x[1:-1], destination) for x in commands]
            cmd = ";".join(commands)
            LOG.debug("Evaluate mel command: %s;", cmd)
            mel.eval(cmd)

    return copied_attributes


def reset(node, attributes=None):
    # type: (str, Optional[Sequence[str]]) -> None
    """Reset the given attributes to their default values.

    If no attributes are specified, all the user-defined attributes of the node
    will be reset to their default values.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> cmds.setAttr(node + ".translateX", 10)
        >>> cmds.setAttr(node + ".scaleX", 3)
        >>> reset(node)
        >>> cmds.getAttr(node + ".translateX")
        0.0
        >>> cmds.getAttr(node + ".scaleX")
        1.0

    Arguments:
        node: The name of the node that contains the attributes to reset.
        attributes: Filter the attributes to copy.
    """
    for attr in attributes or cmds.listAttr(node, keyable=True) or []:
        plug = "{}.{}".format(node, attr)
        if not cmds.getAttr(plug, settable=True):
            continue
        try:
            value = cmds.attributeQuery(attr, node=node, listDefault=True)[0]
            cmds.setAttr(plug, value)
        except RuntimeError:
            LOG.warning("Failed to reset '%s' plug.", plug)


@contextlib.contextmanager
def restore(node):
    # type: (str) -> Generator[None, None, None]
    """Restore the attributes of the node after the execution of the block.

    From python 3.2+, this can also be used as a decorator.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> cmds.setAttr("persp.translate", 0.0, 1.0, 2.0)
        >>> with restore("persp"):
        ...     _ = cmds.file(new=True, force=True)
        >>> cmds.getAttr("persp.translate")[0]
        (0.0, 1.0, 2.0)

    Arguments:
        node: The name of the node to restore.
    """
    cmds.nodePreset(save=(node, node))
    try:
        yield
    finally:
        cmds.nodePreset(load=(node, node))
        cmds.nodePreset(delete=(node, node))


@contextlib.contextmanager
def unlock(
    node,  # type: str
    attributes=None,  # type: Optional[Sequence[str]]
):  # type: (...) -> Generator[Sequence[str], None, None]
    """Temporarily unlock attributes during the execution of the block.

    If no attributes are specified, all the locked attributes of the node will
    be unlocked during the execution.

    From python 3.2+, this can also be used as a decorator.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> plug = node + ".translateX"
        >>> cmds.setAttr(plug, lock=True)
        >>> cmds.setAttr(plug, 1)
        Traceback (most recent call last):
          ...
        RuntimeError
        >>> with unlock(node):
        ...     cmds.setAttr(plug, 1)
        >>> cmds.getAttr(plug, lock=True)
        True

    Arguments:
        node: The node on which the attributes should be unlocked.
        attributes: Filter the attributes to unlock.

    Yields:
        The name of the unlocked attributes.
    """
    attributes = attributes or cmds.listAttr(node, locked=True) or []

    # Store the name of the plugs and their lock status in a dictionary.
    plugs = {}
    for attribute in attributes:
        plug = "{}.{}".format(node, attribute)
        plugs[plug] = cmds.getAttr(plug, lock=True)

    # Execute the context manager.
    for plug in plugs:
        cmds.setAttr(plug, lock=False)
    try:
        yield attributes
    finally:
        for plug, value in plugs.items():
            cmds.setAttr(plug, lock=value)


def find_used_indices(plug):
    # type: (str) -> List[int]
    """Get the index of used elements of an array attribute.

    An element is considered used if it is either connected or have had their
    value set.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> cmds.addAttr(node, longName="test", multi=True)
        >>> cmds.setAttr(node + ".test[0]", 0)
        >>> cmds.setAttr(node + ".test[3]", 0)
        >>> _ = cmds.connectAttr(node + ".translateX", node + ".test[8]")
        >>> find_used_indices(node + ".test")
        [0, 3, 8]

    Arguments:
        plug: The plug to analyse.

    Returns:
        The used indices of the multi attribute.
    """
    sel = OpenMaya.MSelectionList()
    sel.add(plug)
    mplug = sel.getPlug(0)
    return list(mplug.getExistingArrayAttributeIndices())


def find_next_index(plug, start=0):
    # type: (str, int) -> str
    """Find the next available index of a multi attribute.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> src = cmds.createNode("multMatrix", name="src")
        >>> dst = cmds.createNode("multMatrix", name="dst")
        >>> find_next_index(dst + ".matrixIn")
        'dst.matrixIn[0]'
        >>> _ = cmds.connectAttr(src + ".matrixSum", dst + ".matrixIn[0]")
        >>> find_next_index(dst + ".matrixIn")
        'dst.matrixIn[1]'

    Arguments:
        plug: The name of the multi attribute plug.
        start: The index from which the search should be start.

    Returns:
        The next available plug of the multi attribute.
    """
    index = mel.eval("getNextFreeMultiIndex {} {}".format(plug, start))
    return "{}[{}]".format(plug, index)


def delete_user_defined(node, attributes=None, keep_if_connected=False):
    # type: (str, Optional[Sequence[str]], bool) -> List[str]
    """Delete user-defined attributes on the given node.

    If no attributes are specified, all the user-defined attributes of the node
    will be deleted during the execution.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> cmds.addAttr(node, longName="testA")
        >>> cmds.addAttr(node, longName="testB")
        >>> cmds.addAttr(node, longName="testC")
        >>> _ = cmds.connectAttr(node + ".translateX", node + ".testB")
        >>> delete_user_defined(node, keep_if_connected=True)
        ['testA', 'testC']

    Arguments:
        node: The name of the node which contains the attributes.
        attributes: Filter the attributes to delete.
        keep_if_connected: Do not delete the attribute if it has an
            input connection.

    Returns:
        The name of all the deleted attributes.
    """
    deleted = []
    attributes = attributes or cmds.listAttr(node, userDefined=True) or []
    for attribute in attributes:

        # Check if the attribute has some input connections.
        if keep_if_connected:
            plug = "{}.{}".format(node, attribute)
            if cmds.listConnections(plug, source=True, destination=False):
                continue

        # Delete the attribute.
        cmds.deleteAttr(node, attribute=attribute)
        deleted.append(attribute)
    return deleted


def move(plug, where="down"):
    # type: (str, str) -> None
    # pylint: disable=too-many-branches
    """Move the specified attributes along the channel box.

    Only the user's attributes are supported by the function. For example,
    the translateX attribute cannot be moved.

    The supported directions are: ``top``, ``up``, ``down``, ``bottom``.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> for name in "ABCD":
        ...     cmds.addAttr(node, longName=name)
        >>> cmds.listAttr(node, userDefined=True)
        ['A', 'B', 'C', 'D']
        >>> move(node + ".C", where="up")
        >>> cmds.listAttr(node, userDefined=True)
        ['A', 'C', 'B', 'D']
        >>> move(node + ".D", where="top")
        >>> cmds.listAttr(node, userDefined=True)
        ['D', 'A', 'C', 'B']

    Arguments:
        plug: The name of the pug to move.
        where: The direction in which the plug will be moved.

    Raises:
        ValueError: The specifiy direction is not supported.
    """
    node, attribute = plug.split(".", 1)

    def to_last(attr):
        # type: (str) -> None
        # Redirecting the stdout does not seem to be enough to remove the
        # `Undo:` messages. Pytest is able to remove these messages, so it
        # might be worth investigating this to improve the silent utility.
        with maya_tools.io.silent():
            cmds.deleteAttr(node, attribute=attr)
            cmds.undo()

    # Find all the visible user-defined attributes.
    attribute_list = []
    for attribute_ in cmds.listAttr(node, userDefined=True) or []:
        # plug_ = "{}.{}".format(node, attribute_)
        # if not cmds.getAttr(plug_, channelBox=True):
        #     continue
        attribute_list.append(attribute_)
    try:
        index = attribute_list.index(attribute)
    except ValueError:
        LOG.error("The attribute is not an user attribute.")
        return

    with unlock(node):

        if where == "top":
            if attribute == attribute_list[0]:
                return
            for attribute_ in attribute_list:
                if attribute_ != attribute:
                    to_last(attribute_)

        elif where == "up":
            if attribute == attribute_list[0]:
                return
            to_last(attribute_list[index - 1])
            for attribute_ in attribute_list[index + 1 :]:
                to_last(attribute_)

        elif where == "down":
            if attribute == attribute_list[-1]:
                return
            to_last(attribute)
            for attribute_ in attribute_list[index + 2 :]:
                to_last(attribute_)

        elif where == "bottom":
            if attribute == attribute_list[-1]:
                return
            to_last(attribute)

        else:
            raise ValueError("Direction not supported: '{}'.".format(where))


def write_data(node, name, data, compress=False):
    # type: (str, str, Union[List[Any], Dict[str, Any]], bool) -> None
    """Create a maya attribute that contains the given data.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> data = {
        ...     "red": [255, 0, 0],
        ...     "blue": [255, 0, 0],
        ...     "green": [255, 0, 0],
        ... }
        >>> write_data(node, "test", data, compress=True)

    Arguments:
        node: The name of the node on which create the attribute.
        name: The name of the attribute to create.
        data: The data to write on the attribute.
        compress: Compress the given data before writing it to the
            attribute.
    """
    plug = "{}.{}".format(node, name)
    if not cmds.objExists(plug):
        cmds.addAttr(node, longName=name, dataType="string")
    string = str(json.dumps(data))  # type: str
    if compress:
        string_ = bytes(string.encode("utf-8"))
        string = str(codecs.encode(codecs.encode(string_, "zlib"), "base64"))
    cmds.setAttr(plug, string, type="string")


def read_data(plug, compressed=False):
    # type: (str, bool) -> Union[List[Any], Dict[str, Any]]
    """Read the data from an attribute.

    Examples:
        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform")
        >>> cmds.addAttr(node, longName="test", dataType="string")
        >>> data = "eJyrVkrKKU1VslKINjI11VEwAKJYHQWl9KLU1DwM0aLUFFSxWgD58A9D"
        >>> cmds.setAttr(node + ".test", data, type="string")
        >>> result = {
        ...     "red": [255, 0, 0],
        ...     "blue": [255, 0, 0],
        ...     "green": [255, 0, 0],
        ... }
        >>> result == read_data(node + ".test", compressed=True)
        True

    Arguments:
        plug: The name of the plug ot read.
        compressed: Specify if the data to be read is compressed or not.

    Returns:
        The python object decoded.
    """
    string = cmds.getAttr(plug)
    if compressed:
        string = bytes(string.encode("utf-8"))
        string = codecs.decode(codecs.decode(string, "base64"), "zlib")
    data = json.loads(string)  # type: Union[List[Any], Dict[str, Any]]
    return data
