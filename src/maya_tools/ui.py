"""Windows utilities."""
import logging
from typing import Optional

from PySide2 import QtWidgets

from maya import cmds

LOG = logging.getLogger(__name__)


def main_window():  # pragma: no cover
    # type: () -> Optional[QtWidgets.QWidget]
    """Find the maya main application widget.

    When launch in standalone mode, maya does not have any qt application, so
    this function will not return anything.

    Arguments:
        name: The widget name to search.

    Returns:
        The top level widget or None of maya is in standalone mode.
    """
    top = QtWidgets.QApplication.topLevelWidgets()
    return ([w for w in top if w.objectName() == "MayaWindow"] or [None])[0]


def toggle_panel_element(element, panel=None):
    # type: (str, Optional[bool]) -> None
    """Toggles the visibility of an element in the viewport.

    The function simply wraps the :func:`cmds.modelEditor` command to toggle
    the visibility of the specified element in a single line.

    See the `modelEditor`_ command in the official documentation.

    Examples:
        >>> from maya import cmds
        >>> panel = cmds.getPanel(withFocus=True)
        >>> toggle_panel_element("joint")
        >>> cmds.modelEditor(panel, query=True, joint=True)
        False

    Arguments:
        element (str): The UI element to show or hide. This should be a
            parameter of the :func:`cmds.modelEditor` command, e.g. ``joints``.
        panel (str, optional): The panel on which toggles the element.
            By default, operate on the current panel.

    .. _modelEditor:
        https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=__CommandsPython_index_html
    """
    if panel is None:
        panel = cmds.getPanel(withFocus=True)
    state = cmds.modelEditor(panel, query=True, **{element: True})
    cmds.modelEditor(panel, edit=True, **{element: not state})
