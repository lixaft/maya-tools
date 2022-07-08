"""Configure pytest environement."""
import pytest

from maya import cmds


@pytest.fixture(autouse=True)
def new_scene():
    # type: () -> None
    """Create a new scene."""
    cmds.file(new=True, force=True)
    cmds.flushUndo()
