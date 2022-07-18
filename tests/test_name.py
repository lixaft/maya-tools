"""Test name module."""
import pytest

from maya import cmds

import maya_tools.name


def create_conflicts():
    # type: () -> None
    """Create a scene with conflict names."""
    cmds.createNode("transform", name="A")
    cmds.createNode("transform", name="B")
    cmds.createNode("transform", name="B", parent="A")


def test_confclit_names():
    # type: () -> None
    """Test if name conflicts are correctly detected."""
    assert maya_tools.name.find_conflicts() == []
    create_conflicts()
    assert maya_tools.name.find_conflicts() == ["|B", "A|B"]


def test_conflict_names_with_set():
    # type: () -> None
    """Test to create a set that will contains all the conflict names."""
    maya_tools.name.find_conflicts(create_set=True)
    assert not cmds.objExists("CONFLICTS_NODES")
    create_conflicts()
    maya_tools.name.find_conflicts(create_set=True)
    assert cmds.objExists("CONFLICTS_NODES")


def test_conflict_names_set_deletion():
    # type: () -> None
    """Ensure the set deletion if no confclit names is found."""
    create_conflicts()
    maya_tools.name.find_conflicts(create_set=True)
    cmds.delete("A|B")
    maya_tools.name.find_conflicts(create_set=True)
    assert not cmds.objExists("CONFLICTS_NODES")


@pytest.mark.parametrize(
    "value,expected",
    [
        ("nice-name", "Nice Name"),
        ("nice_name", "Nice Name"),
        ("niceName", "Nice Name"),
        ("NiceName", "Nice Name"),
        ("nice name", "Nice Name"),
    ],
)
def test_nice_name_generation(value, expected):
    # type: (str, str) -> None
    """Make sure the generated names are unique across the scene."""
    assert maya_tools.name.nice(value) == expected


def test_generator_unique_name():
    # type: () -> None
    """Ensure that a generate name is unique across the scene."""
    create_conflicts()
    cmds.rename("A|B", "B1")
    assert maya_tools.name.unique("A") == "A1"
    assert maya_tools.name.unique("B") == "B2"


def test_generator_unique_name_with_hash():
    # type: () -> None
    """Ensure that a generate name is unique across the scene."""
    create_conflicts()
    cmds.rename("A|B", "B_000_B")
    assert maya_tools.name.unique("A_###_A") == "A_000_A"
    assert maya_tools.name.unique("B_###_B") == "B_001_B"

    with pytest.raises(NameError):
        maya_tools.name.unique("A_##_##_A")
