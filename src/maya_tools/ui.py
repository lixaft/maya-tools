"""Windows utilities."""
import logging
from typing import Optional

from PySide2 import QtWidgets

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
