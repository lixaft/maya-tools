# pylint: disable=import-outside-toplevel, protected-access
"""Collection of tools and utilities for Autodesk Maya."""
import sys
from types import ModuleType
from typing import List

__all__ = ["__version__", "__version_tuple__", "all_modules"]

__version__ = "0.1.0"
__version_tuple__ = ("0", "1", "0")


def all_modules():
    # type: () -> List[ModuleType]
    """Return all the modules inside the package."""
    import maya_tools._internal
    import maya_tools.api
    import maya_tools.attribute
    import maya_tools.blendshape
    import maya_tools.cleanup
    import maya_tools.color
    import maya_tools.connection
    import maya_tools.constraint
    import maya_tools.container
    import maya_tools.curve
    import maya_tools.deformer
    import maya_tools.hierarchy
    import maya_tools.history
    import maya_tools.io
    import maya_tools.joint
    import maya_tools.mesh
    import maya_tools.name
    import maya_tools.nodeeditor
    import maya_tools.offset
    import maya_tools.performance
    import maya_tools.plugin
    import maya_tools.reference
    import maya_tools.search
    import maya_tools.selection
    import maya_tools.shape
    import maya_tools.skincluster
    import maya_tools.ui
    import maya_tools.visibility
    import maya_tools.wrap

    return [
        maya_tools._internal,
        maya_tools.api,
        maya_tools.attribute,
        maya_tools.blendshape,
        maya_tools.cleanup,
        maya_tools.color,
        maya_tools.connection,
        maya_tools.constraint,
        maya_tools.container,
        maya_tools.curve,
        maya_tools.deformer,
        maya_tools.hierarchy,
        maya_tools.history,
        maya_tools.io,
        maya_tools.joint,
        maya_tools.mesh,
        maya_tools.name,
        maya_tools.nodeeditor,
        maya_tools.offset,
        maya_tools.performance,
        maya_tools.plugin,
        maya_tools.reference,
        maya_tools.search,
        maya_tools.selection,
        maya_tools.shape,
        maya_tools.skincluster,
        maya_tools.ui,
        maya_tools.visibility,
        maya_tools.wrap,
        sys.modules[__name__],
    ]
