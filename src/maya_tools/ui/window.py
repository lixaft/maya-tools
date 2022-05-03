"""Windows utilities."""
import logging

from PySide2 import QtWidgets

LOG = logging.getLogger(__name__)


def find_main():
    # type: () -> QtWidgets.QWidget
    """Find a top level widget with a specified name.

    Arguments:
        name: The widget name to search.

    Returns:
        The top level widget.
    """
    top = QtWidgets.QApplication.topLevelWidgets()
    return ([w for w in top if w.objectName() == "MayaWindow"] or [None])[0]
