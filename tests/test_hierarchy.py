"""Test maya hierarchy."""
import maya_tools.hierarchy


def test_make_with_existing_parent():
    # type: () -> None
    """Test the make function with an existing parent mode."""
    path = "a|b|c"
    maya_tools.hierarchy.make(path)

    path = "a|b|d"
    maya_tools.hierarchy.make(path)
