"""Test for attribute."""
from typing import Any, Dict, List

import pytest

from maya import cmds

import maya_tools.attribute


@pytest.mark.parametrize(
    "attributes",
    [
        [{"longName": "test", "attributeType": "long"}],
        [{"longName": "test", "attributeType": "short"}],
        [{"longName": "test", "attributeType": "bool"}],
        [{"longName": "test", "dataType": "string"}],
        [{"longName": "test", "attributeType": "matrix"}],
        [
            {
                "longName": "test",
                "attributeType": "compound",
                "numberOfChildren": 3,
            },
            {"longName": "testA", "parent": "test"},
            {"longName": "testB", "parent": "test"},
            {
                "longName": "testC",
                "parent": "test",
                "attributeType": "compound",
                "numberOfChildren": 2,
            },
            {"longName": "testCA", "parent": "testC"},
            {"longName": "testCB", "parent": "testC"},
        ],
        [{"longName": "test", "attributeType": "short", "multi": True}],
    ],
    ids=["long", "short", "bool", "string", "matrix", "compound", "multi"],
)
def test_copy_types(attributes):
    # type: (List[Dict[str, Any]]) -> None
    """Test to copy simple attribute types."""
    src = cmds.createNode("transform")
    dst = cmds.createNode("transform")

    # Create the attributes.
    for flags in attributes:
        cmds.addAttr(src, **flags)

    # Perform the copy.
    maya_tools.attribute.copy(src, dst, values=True)

    # Compare the attributes.
    for flags in attributes:
        src_plug = "{}.{}".format(src, flags["longName"])
        dst_plug = "{}.{}".format(dst, flags["longName"])
        assert cmds.objExists(dst_plug)
        if flags.get("attributeType") != "compound":
            assert cmds.getAttr(src_plug) == cmds.getAttr(dst_plug)


def test_copy_existing():
    # type: () -> None
    """Test to copy an attribute that already exists on the destination."""
    src = cmds.createNode("transform")
    dst = cmds.createNode("transform")

    cmds.addAttr(src, longName="test")
    cmds.addAttr(dst, longName="test")

    maya_tools.attribute.copy(src, dst)

    with pytest.raises(AttributeError):
        maya_tools.attribute.copy(src, dst, fatal=True)


def test_add_separator():
    # type: () -> None
    """Test to create separator attributes."""
    node = cmds.createNode("transform", name="test")

    plug = maya_tools.attribute.add_separator(node)
    assert plug == "test.separator00"
    plug = maya_tools.attribute.add_separator(node)
    assert plug == "test.separator01"

    plug = maya_tools.attribute.add_separator(node, name="divider{index}")
    assert plug == "test.divider0"
    plug = maya_tools.attribute.add_separator(node, name="divider{index}")
    assert plug == "test.divider1"

    with pytest.raises(ValueError):
        maya_tools.attribute.add_separator(node, name="divider")


@pytest.mark.parametrize(
    "attributes",
    [None, ["worldMatrix[0]"]],
    ids=["locked", "multi"],
)
def test_invalid_reset(attributes):
    # type: (Any) -> None
    """Test invalid case of the reset function."""
    node = cmds.createNode("transform")
    cmds.setAttr(node + ".translateX", lock=True)
    maya_tools.attribute.reset(node, attributes=attributes)


def test_move_attribute():
    # type: () -> None
    """Test to move an attribute aloung the channel box."""
    node = cmds.createNode("transform")
    cmds.addAttr(node, longName="A")
    cmds.addAttr(node, longName="B")
    cmds.addAttr(node, longName="C")
    cmds.addAttr(node, longName="D")
    cmds.addAttr(node, longName="E")

    # Valid case.
    maya_tools.attribute.move(node + ".A", where="bottom")
    assert cmds.listAttr(userDefined=True) == ["B", "C", "D", "E", "A"]
    maya_tools.attribute.move(node + ".E", where="top")
    assert cmds.listAttr(userDefined=True) == ["E", "B", "C", "D", "A"]
    maya_tools.attribute.move(node + ".C", where="up")
    assert cmds.listAttr(userDefined=True) == ["E", "C", "B", "D", "A"]
    maya_tools.attribute.move(node + ".B", where="down")
    assert cmds.listAttr(userDefined=True) == ["E", "C", "D", "B", "A"]

    # Invalid case.
    maya_tools.attribute.move(node + ".E", where="top")
    assert cmds.listAttr(userDefined=True) == ["E", "C", "D", "B", "A"]
    maya_tools.attribute.move(node + ".E", where="up")
    assert cmds.listAttr(userDefined=True) == ["E", "C", "D", "B", "A"]
    maya_tools.attribute.move(node + ".A", where="down")
    assert cmds.listAttr(userDefined=True) == ["E", "C", "D", "B", "A"]
    maya_tools.attribute.move(node + ".A", where="bottom")
    assert cmds.listAttr(userDefined=True) == ["E", "C", "D", "B", "A"]

    with pytest.raises(ValueError):
        maya_tools.attribute.move(node + ".A", where="invalid")
    maya_tools.attribute.move(node + ".translateX", where="up")
